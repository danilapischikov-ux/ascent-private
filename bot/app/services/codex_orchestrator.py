from __future__ import annotations

from typing import Any
from uuid import uuid4

import httpx

from app.core.config import Settings
from app.services.codex_decision_safety import (
    CodexDecision,
    DecisionValidationResult,
    SafetyPolicy,
    validate_codex_decision,
)


SYSTEM_INSTRUCTIONS = """
You are the AscentPrivate marketing decision engine. Return only a structured JSON object that
matches the supplied schema. Do not include personal data. Prefer keep/manual_review when data is
thin, tracking is unstable, or compliance is unclear. Never propose increasing total approved budget.
"""


class CodexOrchestrator:
    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None) -> None:
        self.settings = settings
        self.client = client or httpx.AsyncClient(timeout=settings.openai_decision_timeout_seconds)

    async def run_decision(
        self,
        *,
        segment_context: dict[str, Any],
        policy: SafetyPolicy | None = None,
    ) -> DecisionValidationResult:
        response_payload = await self._call_responses_api(segment_context)
        decision_payload = extract_response_json(response_payload)
        return validate_codex_decision(decision_payload, policy)

    async def _call_responses_api(self, segment_context: dict[str, Any]) -> dict[str, Any]:
        if not self.settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required to run Codex decisions")

        request_id = f"ascent-decision-{uuid4().hex}"
        response = await self.client.post(
            "https://api.openai.com/v1/responses",
            headers={
                "Authorization": f"Bearer {self.settings.openai_api_key}",
                "Content-Type": "application/json",
                "X-Client-Request-Id": request_id,
            },
            json={
                "model": self.settings.openai_decision_model,
                "instructions": SYSTEM_INSTRUCTIONS,
                "input": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": (
                                    "Analyze this PII-free marketing segment context and return one "
                                    f"bounded decision JSON:\n{segment_context}"
                                ),
                            }
                        ],
                    }
                ],
                "text": {
                    "format": {
                        "type": "json_schema",
                        "name": "ascent_codex_decision",
                        "strict": True,
                        "schema": CodexDecision.model_json_schema(),
                    }
                },
            },
        )
        response.raise_for_status()
        return response.json()


def extract_response_json(response_payload: dict[str, Any]) -> dict[str, Any]:
    for item in response_payload.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"} and content.get("text"):
                import json

                return json.loads(content["text"])
            if content.get("type") == "output_json" and content.get("json"):
                return dict(content["json"])
    raise ValueError("OpenAI response did not contain structured decision JSON")
