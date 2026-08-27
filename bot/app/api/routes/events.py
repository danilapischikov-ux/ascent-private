from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.events import SiteEventRequest, SiteEventResponse
from app.db.repositories import analytics as analytics_repo
from app.db.session import get_db_session

router = APIRouter(prefix="/api/events", tags=["analytics"])


def _client_ip(request: Request) -> str | None:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",", maxsplit=1)[0].strip()
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()
    return request.client.host if request.client else None


@router.post("", response_model=SiteEventResponse)
async def collect_site_event(
    payload: SiteEventRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> SiteEventResponse:
    attribution = payload.attribution.model_dump(exclude_none=True) if payload.attribution else None
    event, stored = await analytics_repo.create_site_event(
        session,
        event_id=payload.event_id,
        event_type=payload.event_type or payload.event_name or "unknown",
        occurred_at=payload.occurred_at,
        lead_id=payload.lead_id,
        session_id=payload.session_id,
        client_id=payload.client_id,
        yclid=payload.yclid or (attribution or {}).get("yclid"),
        payment_token=payload.payment_token,
        telegram_user_id=payload.telegram_user_id,
        url=payload.url,
        referrer=payload.referrer,
        user_agent=request.headers.get("user-agent"),
        ip_address=_client_ip(request),
        attribution=attribution,
        payload=payload.payload,
    )
    await session.commit()
    return SiteEventResponse(event_id=event.event_id, stored=stored)
