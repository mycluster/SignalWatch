"""Schemas for normalized event API responses."""
# ruff: noqa: UP045

from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class EventSummary(BaseModel):
    """Compact normalized event shape for list responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    source_event_id: str
    event_timestamp: Optional[datetime] = None
    country_code: Optional[str] = None
    event_category: str
    domain: str
    is_supply_chain_related: bool
    avg_tone: Optional[float] = None
    source_url: Optional[str] = None


class EventListResponse(BaseModel):
    """Paginated normalized event response."""

    count: int
    limit: int
    offset: int
    events: list[EventSummary]


class EventDetail(BaseModel):
    """Full normalized event detail for drill-down/debug views."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    source_system: str
    source_event_id: str
    source_file_path: Optional[str] = None
    source_url: Optional[str] = None
    raw_record_hash: str
    event_date: Optional[date] = None
    event_timestamp: Optional[datetime] = None
    country_code: Optional[str] = None
    country_name: Optional[str] = None
    admin_region: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    geo_precision: Optional[str] = None
    event_code: Optional[str] = None
    event_root_code: Optional[str] = None
    event_category: str
    event_subcategory: Optional[str] = None
    domain: str
    actor_1_name: Optional[str] = None
    actor_1_country_code: Optional[str] = None
    actor_1_type: Optional[str] = None
    actor_2_name: Optional[str] = None
    actor_2_country_code: Optional[str] = None
    actor_2_type: Optional[str] = None
    goldstein_score: Optional[float] = None
    avg_tone: Optional[float] = None
    source_count: Optional[int] = None
    mention_count: Optional[int] = None
    article_count: Optional[int] = None
    is_supply_chain_related: bool
    supply_chain_relevance_score: Optional[float] = None
    confidence_score: Optional[float] = None
    pipeline_run_id: Optional[UUID] = None
    ingested_at: Optional[datetime] = None
    normalized_at: datetime
    created_at: datetime
    updated_at: datetime
