"""Database access for pipeline observability."""

from __future__ import annotations

from typing import Any, Callable

import psycopg
from psycopg.rows import dict_row

from signalwatch.core.config import settings


class PipelineService:
    """Query pipeline run health."""

    def __init__(
        self,
        database_url: str | None = None,
        connection_factory: Callable[..., Any] | None = None,
    ) -> None:
        self.database_url = database_url or settings.database_url
        self._connection_factory = connection_factory or psycopg.connect

    def get_health(self) -> dict[str, Any]:
        """Return latest pipeline status and movement counts."""
        with self._connect() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    SELECT pipeline_name, status, finished_at, records_read,
                        records_written, records_failed
                    FROM pipeline_runs
                    ORDER BY started_at DESC, created_at DESC
                    LIMIT 1
                    """
                )
                latest_run = cursor.fetchone()
                cursor.execute(
                    """
                    SELECT MAX(finished_at) AS latest_successful_run
                    FROM pipeline_runs
                    WHERE status = 'success'
                    """
                )
                latest_success = cursor.fetchone()

        if not latest_run:
            return {
                "status": "unknown",
                "latest_pipeline": None,
                "latest_successful_run": None,
                "records_read": 0,
                "records_written": 0,
                "records_failed": 0,
            }

        return {
            "status": _health_status(latest_run),
            "latest_pipeline": latest_run["pipeline_name"],
            "latest_successful_run": latest_success["latest_successful_run"],
            "records_read": latest_run["records_read"] or 0,
            "records_written": latest_run["records_written"] or 0,
            "records_failed": latest_run["records_failed"] or 0,
        }

    def _connect(self) -> Any:
        return self._connection_factory(self.database_url)


def _health_status(latest_run: dict[str, Any]) -> str:
    if latest_run["status"] == "failure":
        return "unhealthy"
    if latest_run["records_failed"]:
        return "degraded"
    if latest_run["status"] in {"success", "skipped"}:
        return "healthy"
    return "unknown"
