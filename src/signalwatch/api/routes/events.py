"""Normalized events API routes."""
# ruff: noqa: UP045

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from signalwatch.api.schemas.events import EventDetail, EventListResponse, EventSummary
from signalwatch.api.services.event_service import EventService

router = APIRouter(tags=["events"])


def get_event_service() -> EventService:
    """Return event service dependency."""
    return EventService()


EVENT_SERVICE_DEPENDENCY = Depends(get_event_service)


@router.get("/events", response_model=EventListResponse)
async def list_events(
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    country_code: Optional[str] = None,
    event_category: Optional[str] = None,
    domain: Optional[str] = None,
    is_supply_chain_related: Optional[bool] = None,
    since: Optional[datetime] = None,
    until: Optional[datetime] = None,
    event_service: EventService = EVENT_SERVICE_DEPENDENCY,
) -> EventListResponse:
    """Return paginated normalized events."""
    events = event_service.list_events(
        limit=limit,
        offset=offset,
        country_code=country_code,
        event_category=event_category,
        domain=domain,
        is_supply_chain_related=is_supply_chain_related,
        since=since,
        until=until,
    )
    return EventListResponse(
        count=len(events),
        limit=limit,
        offset=offset,
        events=[EventSummary.model_validate(event) for event in events],
    )


@router.get("/events/{event_id}", response_model=EventDetail)
async def get_event(
    event_id: UUID,
    event_service: EventService = EVENT_SERVICE_DEPENDENCY,
) -> EventDetail:
    """Return full normalized event detail."""
    event = event_service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return EventDetail.model_validate(event)
