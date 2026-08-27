from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from decimal import Decimal
from enum import StrEnum
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator
from sqlalchemy import bindparam, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession


class ProposedAction(StrEnum):
    KEEP = "keep"
    REDUCE_BID = "reduce_bid"
    PAUSE_AD = "pause_ad"
    PAUSE_KEYWORD = "pause_keyword"
    ADD_NEGATIVE_KEYWORD = "add_negative_keyword"
    BUDGET_SHIFT = "budget_shift"
    CREATE_DRAFT_AD = "create_draft_ad"
    MANUAL_REVIEW = "manual_review"


WRITE_ACTIONS = frozenset(
    {
        ProposedAction.REDUCE_BID,
        ProposedAction.PAUSE_AD,
        ProposedAction.PAUSE_KEYWORD,
        ProposedAction.ADD_NEGATIVE_KEYWORD,
        ProposedAction.BUDGET_SHIFT,
        ProposedAction.CREATE_DRAFT_AD,
    }
)
NON_WRITE_ACTIONS = frozenset({ProposedAction.KEEP, ProposedAction.MANUAL_REVIEW})
ALLOWED_ACTIONS = WRITE_ACTIONS | NON_WRITE_ACTIONS


class DataWindow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    start: date
    end: date

    @model_validator(mode="after")
    def validate_order(self) -> "DataWindow":
        if self.end < self.start:
            raise ValueError("data_window.end must be greater than or equal to data_window.start")
        return self


class RollbackPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: str = Field(min_length=1, max_length=64)
    payload: dict[str, Any] = Field(default_factory=dict)
    operator_note: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def validate_payload(self) -> "RollbackPlan":
        if not self.payload:
            raise ValueError("rollback_plan.payload is required for write actions")
        return self


class CodexDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision_id: str = Field(min_length=8, max_length=128)
    segment_id: str = Field(min_length=1, max_length=128)
    data_window: DataWindow
    sample_size: int = Field(ge=0)
    reason_codes: list[str] = Field(default_factory=list, max_length=20)
    proposed_action: ProposedAction
    change_value: dict[str, Any] = Field(default_factory=dict)
    confidence: Decimal = Field(ge=Decimal("0"), le=Decimal("1"))
    rollback_plan: RollbackPlan | None = None
    compliance_flag: bool = False
    target_ids: list[str] = Field(default_factory=list, max_length=500)
    affected_entities_count: int | None = Field(default=None, ge=0)
    current_bid: Decimal | None = Field(default=None, ge=Decimal("0"))
    proposed_bid: Decimal | None = Field(default=None, ge=Decimal("0"))
    budget_delta_rub: Decimal = Decimal("0")
    previous_state: dict[str, Any] = Field(default_factory=dict)
    proposed_state: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("reason_codes", "target_ids")
    @classmethod
    def validate_non_empty_items(cls, value: list[str]) -> list[str]:
        if any(not item.strip() for item in value):
            raise ValueError("list values must be non-empty strings")
        return value

    @model_validator(mode="after")
    def normalize_affected_count(self) -> "CodexDecision":
        if self.affected_entities_count is None:
            self.affected_entities_count = len(self.target_ids)
        return self


class DecisionValidationStatus(StrEnum):
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass(frozen=True)
class SafetyPolicy:
    min_sample_size: int = 30
    min_write_confidence: Decimal = Decimal("0.70")
    max_write_entities: int = 1
    max_bid_reduction_ratio: Decimal = Decimal("0.50")
    max_abs_budget_shift_rub: Decimal = Decimal("1000.00")
    allow_positive_budget_delta: bool = False
    allowed_actions: frozenset[ProposedAction] = field(default_factory=lambda: ALLOWED_ACTIONS)


class DecisionValidationResult(BaseModel):
    status: DecisionValidationStatus
    decision: CodexDecision | None = None
    errors: list[str] = Field(default_factory=list)
    manual_review_required: bool = False

    @property
    def is_approved(self) -> bool:
        return self.status == DecisionValidationStatus.APPROVED


class DryRunExecutionResult(BaseModel):
    action_id: str
    decision_id: str | None = None
    dry_run: Literal[True] = True
    validation: DecisionValidationResult
    persisted: bool


def validate_codex_decision(payload: CodexDecision | dict[str, Any], policy: SafetyPolicy | None = None) -> DecisionValidationResult:
    policy = policy or SafetyPolicy()
    errors: list[str] = []

    try:
        decision = payload if isinstance(payload, CodexDecision) else CodexDecision.model_validate(payload)
    except ValidationError as exc:
        return DecisionValidationResult(
            status=DecisionValidationStatus.REJECTED,
            errors=[f"{'.'.join(str(part) for part in error['loc'])}: {error['msg']}" for error in exc.errors()],
            manual_review_required=True,
        )

    if decision.proposed_action not in policy.allowed_actions:
        errors.append(f"action '{decision.proposed_action}' is not allow-listed")

    if decision.compliance_flag and decision.proposed_action != ProposedAction.MANUAL_REVIEW:
        errors.append("compliance_flag decisions must use proposed_action='manual_review'")

    if decision.sample_size < policy.min_sample_size and decision.proposed_action not in NON_WRITE_ACTIONS:
        errors.append(
            f"sample_size={decision.sample_size} is below min_sample_size={policy.min_sample_size} for write actions"
        )

    if decision.proposed_action in WRITE_ACTIONS:
        _validate_write_decision(decision, policy, errors)

    status = DecisionValidationStatus.REJECTED if errors else DecisionValidationStatus.APPROVED
    return DecisionValidationResult(
        status=status,
        decision=decision,
        errors=errors,
        manual_review_required=bool(errors) or decision.proposed_action == ProposedAction.MANUAL_REVIEW,
    )


def _validate_write_decision(decision: CodexDecision, policy: SafetyPolicy, errors: list[str]) -> None:
    if decision.confidence < policy.min_write_confidence:
        errors.append(f"confidence={decision.confidence} is below min_write_confidence={policy.min_write_confidence}")

    if decision.rollback_plan is None:
        errors.append("rollback_plan is required for write actions")

    affected_count = decision.affected_entities_count or 0
    if affected_count < 1:
        errors.append("write actions must affect at least one explicit entity")
    if affected_count > policy.max_write_entities:
        errors.append(f"affected_entities_count={affected_count} exceeds max_write_entities={policy.max_write_entities}")

    if len(decision.target_ids) > policy.max_write_entities:
        errors.append(f"target_ids count={len(decision.target_ids)} exceeds max_write_entities={policy.max_write_entities}")

    if decision.proposed_action == ProposedAction.REDUCE_BID:
        _validate_reduce_bid(decision, policy, errors)

    if decision.proposed_action == ProposedAction.BUDGET_SHIFT:
        _validate_budget_shift(decision, policy, errors)


def _validate_reduce_bid(decision: CodexDecision, policy: SafetyPolicy, errors: list[str]) -> None:
    current_bid = decision.current_bid
    proposed_bid = decision.proposed_bid

    if current_bid is None:
        current_bid = _decimal_from_change_value(decision.change_value, "current_bid")
    if proposed_bid is None:
        proposed_bid = _decimal_from_change_value(decision.change_value, "proposed_bid")

    if current_bid is None or proposed_bid is None:
        errors.append("reduce_bid requires current_bid and proposed_bid")
        return

    if current_bid <= 0:
        errors.append("reduce_bid requires current_bid greater than zero")
        return

    if proposed_bid <= 0:
        errors.append("reduce_bid requires proposed_bid greater than zero")
    if proposed_bid >= current_bid:
        errors.append("reduce_bid cannot increase or keep the current bid")

    reduction_ratio = (current_bid - proposed_bid) / current_bid
    if reduction_ratio > policy.max_bid_reduction_ratio:
        errors.append(
            f"bid reduction ratio={reduction_ratio:.2f} exceeds max_bid_reduction_ratio={policy.max_bid_reduction_ratio}"
        )


def _validate_budget_shift(decision: CodexDecision, policy: SafetyPolicy, errors: list[str]) -> None:
    budget_delta = decision.budget_delta_rub
    if budget_delta == 0:
        budget_delta = _decimal_from_change_value(decision.change_value, "budget_delta_rub") or Decimal("0")

    if budget_delta > 0 and not policy.allow_positive_budget_delta:
        errors.append("positive budget_delta_rub requires manual approval")

    if abs(budget_delta) > policy.max_abs_budget_shift_rub:
        errors.append(
            f"abs(budget_delta_rub)={abs(budget_delta)} exceeds max_abs_budget_shift_rub={policy.max_abs_budget_shift_rub}"
        )


def _decimal_from_change_value(change_value: dict[str, Any], key: str) -> Decimal | None:
    value = change_value.get(key)
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except Exception:
        return None


class CodexDryRunExecutor:
    def __init__(self, policy: SafetyPolicy | None = None) -> None:
        self.policy = policy or SafetyPolicy()

    async def execute(
        self,
        session: AsyncSession,
        payload: CodexDecision | dict[str, Any],
        *,
        raw_response: dict[str, Any] | None = None,
    ) -> DryRunExecutionResult:
        validation = validate_codex_decision(payload, self.policy)
        decision = validation.decision
        action_id = f"dryrun_{uuid4().hex}"

        await self._persist_decision(session, validation, raw_response=raw_response)
        await self._persist_action_log(session, action_id, validation)

        return DryRunExecutionResult(
            action_id=action_id,
            decision_id=decision.decision_id if decision else None,
            validation=validation,
            persisted=True,
        )

    async def _persist_decision(
        self,
        session: AsyncSession,
        validation: DecisionValidationResult,
        *,
        raw_response: dict[str, Any] | None,
    ) -> None:
        decision = validation.decision
        row = {
            "decision_id": decision.decision_id if decision else f"invalid_{uuid4().hex}",
            "segment_id": decision.segment_id if decision else None,
            "data_window": _json_dump(decision.data_window) if decision else None,
            "sample_size": decision.sample_size if decision else None,
            "reason_codes": decision.reason_codes if decision else [],
            "proposed_action": decision.proposed_action.value if decision else None,
            "change_value": _json_dump(decision.change_value) if decision else {},
            "confidence": str(decision.confidence) if decision else None,
            "rollback_plan": _json_dump(decision.rollback_plan) if decision and decision.rollback_plan else None,
            "compliance_flag": decision.compliance_flag if decision else False,
            "target_ids": decision.target_ids if decision else [],
            "status": validation.status.value,
            "validation_status": validation.status.value,
            "validation_errors": validation.errors,
            "manual_review_required": validation.manual_review_required,
            "raw_decision": _json_dump(decision) if decision else {},
            "raw_response": raw_response or {},
            "created_at": _utcnow(),
        }
        await _insert_dynamic(session, "codex_decisions", row)

    async def _persist_action_log(
        self,
        session: AsyncSession,
        action_id: str,
        validation: DecisionValidationResult,
    ) -> None:
        decision = validation.decision
        row = {
            "action_id": action_id,
            "decision_id": decision.decision_id if decision else None,
            "proposed_action": decision.proposed_action.value if decision else "invalid_decision",
            "status": "dry_run_approved" if validation.is_approved else "dry_run_rejected",
            "dry_run": True,
            "target_ids": decision.target_ids if decision else [],
            "previous_state": _json_dump(decision.previous_state) if decision else {},
            "new_state": _json_dump(decision.proposed_state) if decision else {},
            "proposed_state": _json_dump(decision.proposed_state) if decision else {},
            "rollback_payload": _json_dump(decision.rollback_plan.payload) if decision and decision.rollback_plan else None,
            "validation_result": validation.model_dump(mode="json"),
            "error_message": "; ".join(validation.errors) if validation.errors else None,
            "created_at": _utcnow(),
        }
        await _insert_dynamic(session, "action_log", row)


async def _insert_dynamic(session: AsyncSession, table_name: str, row: dict[str, Any]) -> None:
    columns = await _existing_columns(session, table_name)
    if not columns:
        raise RuntimeError(f"Required analytics table '{table_name}' does not exist or has no visible columns")

    insertable = {key: value for key, value in row.items() if key in columns}
    if not insertable:
        raise RuntimeError(f"Analytics table '{table_name}' has no supported columns")

    column_sql = ", ".join(f'"{column}"' for column in insertable)
    value_sql = ", ".join(f":{column}" for column in insertable)
    statement = text(f'INSERT INTO "{table_name}" ({column_sql}) VALUES ({value_sql})')
    json_bind_params = [
        bindparam(column, type_=JSONB)
        for column, value in insertable.items()
        if isinstance(value, (dict, list))
    ]
    if json_bind_params:
        statement = statement.bindparams(*json_bind_params)

    await session.execute(statement, insertable)


async def _existing_columns(session: AsyncSession, table_name: str) -> set[str]:
    result = await session.execute(
        text(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = current_schema()
              AND table_name = :table_name
            """
        ),
        {"table_name": table_name},
    )
    return {row[0] for row in result.fetchall()}


def _json_dump(value: BaseModel | dict[str, Any] | None) -> dict[str, Any] | None:
    if value is None:
        return None
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    return value


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)
