"""Canonical normalized event model."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from uuid import NAMESPACE_URL, UUID, uuid5

from packages.signalwatch_common.enums import Domain, EventCategory


@dataclass(frozen=True)
class NormalizedEvent:
    """Normalized event record ready for persistence."""

    source_event_id: str
    raw_record_hash: str
    event_category: EventCategory
    id: UUID = field(init=False)
    source_system: str = "GDELT"
    source_file_path: str | None = None
    source_url: str | None = None
    event_date: date | None = None
    event_timestamp: datetime | None = None
    country_code: str | None = None
    country_name: str | None = None
    admin_region: str | None = None
    city: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    geo_precision: str | None = None
    event_code: str | None = None
    event_root_code: str | None = None
    event_subcategory: str | None = None
    domain: Domain = Domain.GENERAL
    supply_chain_relevance_score: float | None = None
    actor_1_name: str | None = None
    actor_1_country_code: str | None = None
    actor_1_type: str | None = None
    actor_2_name: str | None = None
    actor_2_country_code: str | None = None
    actor_2_type: str | None = None
    goldstein_score: float | None = None
    avg_tone: float | None = None
    source_count: int | None = None
    mention_count: int | None = None
    article_count: int | None = None
    is_supply_chain_related: bool = False
    confidence_score: float | None = None
    duplicate_group_id: str | None = None
    normalized_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        stable_id = uuid5(NAMESPACE_URL, f"{self.source_system}:{self.source_event_id}")
        object.__setattr__(self, "id", stable_id)
