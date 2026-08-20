"""Persist normalized events to Postgres."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any, Callable
from uuid import UUID

import psycopg
from packages.signalwatch_common.models.normalized_event import NormalizedEvent

from signalwatch.core.config import settings

NORMALIZED_EVENT_COLUMNS = (
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
    "supply_chain_relevance_score",
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
    "confidence_score",
    "pipeline_run_id",
    "normalized_at",
)


class NormalizedEventWriter:
    """Upsert normalized events into Postgres."""

    def __init__(
        self,
        database_url: str | None = None,
        connection_factory: Callable[..., Any] | None = None,
        schema_path: str | Path = "sql/normalized_events.sql",
    ) -> None:
        self.database_url = database_url or settings.database_url
        self._connection_factory = connection_factory or psycopg.connect
        self.schema_path = Path(schema_path)

    def ensure_schema(self) -> None:
        """Create the normalized events table and indexes when missing."""
        schema_sql = self.schema_path.read_text(encoding="utf-8")
        with self._connect() as connection:
            with connection.cursor() as cursor:
                for statement in _split_sql_statements(schema_sql):
                    cursor.execute(statement)

    def upsert_events(
        self,
        events: Iterable[NormalizedEvent],
        pipeline_run_id: UUID | None = None,
    ) -> int:
        """Insert or update events and return rows affected."""
        event_list = list(events)
        if not event_list:
            return 0

        statement = _build_upsert_statement()
        parameters = [_event_parameters(event, pipeline_run_id) for event in event_list]
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.executemany(statement, parameters)
                return cursor.rowcount

    def _connect(self) -> Any:
        return self._connection_factory(self.database_url)


def _build_upsert_statement() -> str:
    placeholders = ", ".join(["%s"] * len(NORMALIZED_EVENT_COLUMNS))
    columns = ", ".join(NORMALIZED_EVENT_COLUMNS)
    update_assignments = ", ".join(
        f"{column} = EXCLUDED.{column}"
        for column in NORMALIZED_EVENT_COLUMNS
        if column not in {"id", "source_system", "source_event_id"}
    )
    return f"""
        INSERT INTO normalized_events ({columns})
        VALUES ({placeholders})
        ON CONFLICT (source_system, source_event_id)
        DO UPDATE SET {update_assignments}, updated_at = NOW()
    """


def _split_sql_statements(schema_sql: str) -> list[str]:
    return [statement.strip() for statement in schema_sql.split(";") if statement.strip()]


def _event_parameters(
    event: NormalizedEvent,
    pipeline_run_id: UUID | None,
) -> tuple[Any, ...]:
    return (
        event.id,
        event.source_system,
        event.source_event_id,
        event.source_file_path,
        event.source_url,
        event.raw_record_hash,
        event.event_date,
        event.event_timestamp,
        event.country_code,
        event.country_name,
        event.admin_region,
        event.city,
        event.latitude,
        event.longitude,
        event.geo_precision,
        event.event_code,
        event.event_root_code,
        event.event_category.value,
        event.event_subcategory,
        event.domain.value,
        event.supply_chain_relevance_score,
        event.actor_1_name,
        event.actor_1_country_code,
        event.actor_1_type,
        event.actor_2_name,
        event.actor_2_country_code,
        event.actor_2_type,
        event.goldstein_score,
        event.avg_tone,
        event.source_count,
        event.mention_count,
        event.article_count,
        event.is_supply_chain_related,
        event.confidence_score,
        pipeline_run_id,
        event.normalized_at,
    )
