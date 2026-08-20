"""Database access for normalized events."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Callable
from uuid import UUID

import psycopg
from psycopg.rows import dict_row

from signalwatch.core.config import settings

EVENT_SUMMARY_COLUMNS = (
    "id",
    "source_event_id",
    "event_timestamp",
    "country_code",
    "event_category",
    "domain",
    "is_supply_chain_related",
    "avg_tone",
    "source_url",
)

EVENT_DETAIL_COLUMNS = (
    "id",
    "source_system",
    "source_event_id",
    "source_file_path",
    "source_url",
    "raw_record_hash",
    "event_date",
    "event_timestamp",
    "country_code",
    "country_name",
    "admin_region",
    "city",
    "latitude",
    "longitude",
    "geo_precision",
    "event_code",
    "event_root_code",
    "event_category",
    "event_subcategory",
    "domain",
    "actor_1_name",
    "actor_1_country_code",
    "actor_1_type",
    "actor_2_name",
    "actor_2_country_code",
    "actor_2_type",
    "goldstein_score",
    "avg_tone",
    "source_count",
    "mention_count",
    "article_count",
    "is_supply_chain_related",
    "supply_chain_relevance_score",
    "confidence_score",
    "pipeline_run_id",
    "ingested_at",
    "normalized_at",
    "created_at",
    "updated_at",
)


class EventService:
    """Query normalized events."""

    def __init__(
        self,
        database_url: str | None = None,
        connection_factory: Callable[..., Any] | None = None,
    ) -> None:
        self.database_url = database_url or settings.database_url
        self._connection_factory = connection_factory or psycopg.connect

    def list_events(
        self,
        *,
        limit: int,
        offset: int,
        country_code: str | None = None,
        event_category: str | None = None,
        domain: str | None = None,
        is_supply_chain_related: bool | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """Return paginated normalized events matching filters."""
        where_sql, parameters = _build_filters(
            country_code=country_code,
            event_category=event_category,
            domain=domain,
            is_supply_chain_related=is_supply_chain_related,
            since=since,
            until=until,
        )
        parameters.extend([limit, offset])
        query = f"""
            SELECT {", ".join(EVENT_SUMMARY_COLUMNS)}
            FROM normalized_events
            {where_sql}
            ORDER BY event_timestamp DESC NULLS LAST, source_event_id
            LIMIT %s OFFSET %s
        """
        with self._connect() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute(query, parameters)
                return list(cursor.fetchall())

    def get_event(self, event_id: UUID) -> dict[str, Any] | None:
        """Return one normalized event by id."""
        query = f"""
            SELECT {", ".join(EVENT_DETAIL_COLUMNS)}
            FROM normalized_events
            WHERE id = %s
        """
        with self._connect() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute(query, (event_id,))
                return cursor.fetchone()

    def _connect(self) -> Any:
        return self._connection_factory(self.database_url)


def _build_filters(
    *,
    country_code: str | None,
    event_category: str | None,
    domain: str | None,
    is_supply_chain_related: bool | None,
    since: datetime | None,
    until: datetime | None,
) -> tuple[str, list[Any]]:
    filters = []
    parameters: list[Any] = []
    if country_code:
        filters.append("country_code = %s")
        parameters.append(country_code)
    if event_category:
        filters.append("event_category = %s")
        parameters.append(event_category)
    if domain:
        filters.append("domain = %s")
        parameters.append(domain)
    if is_supply_chain_related is not None:
        filters.append("is_supply_chain_related = %s")
        parameters.append(is_supply_chain_related)
    if since:
        filters.append("event_timestamp >= %s")
        parameters.append(since)
    if until:
        filters.append("event_timestamp <= %s")
        parameters.append(until)

    if not filters:
        return "", parameters
    return f"WHERE {' AND '.join(filters)}", parameters
