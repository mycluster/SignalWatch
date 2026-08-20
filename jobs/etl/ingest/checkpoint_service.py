"""Postgres-backed checkpoint management for ETL ingestion windows."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Callable
from uuid import UUID, uuid4

import psycopg

from signalwatch.core.config import settings


class CheckpointService:
    """Track pipeline runs and the last successfully processed source window."""

    def __init__(
        self,
        database_url: str | None = None,
        connection_factory: Callable[..., Any] | None = None,
    ) -> None:
        self.database_url = database_url or settings.database_url
        self._connection_factory = connection_factory or psycopg.connect

    def ensure_schema(self, schema_path: str | Path = "sql/pipeline_runs.sql") -> None:
        """Create pipeline-run tracking tables when missing."""
        schema_sql = Path(schema_path).read_text(encoding="utf-8")
        with self._connect() as connection:
            with connection.cursor() as cursor:
                for statement in _split_sql_statements(schema_sql):
                    cursor.execute(statement)

    def start_run(
        self,
        pipeline_name: str,
        source_system: str,
        source_window_start: datetime | None = None,
        source_window_end: datetime | None = None,
    ) -> UUID:
        """Create a running record and return its identifier."""
        run_id = uuid4()
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
					INSERT INTO pipeline_runs (
						id, pipeline_name, source_system,
						source_window_start, source_window_end, status
					) VALUES (%s, %s, %s, %s, %s, 'running')
					""",
                    (
                        run_id,
                        pipeline_name,
                        source_system,
                        source_window_start,
                        source_window_end,
                    ),
                )
        return run_id

    def mark_success(
        self,
        run_id: UUID,
        source_url: str | None = None,
        raw_output_path: str | None = None,
        normalized_output_path: str | None = None,
        storage_backend: str | None = None,
        file_size_bytes: int | None = None,
        records_read: int = 0,
        records_written: int = 0,
        records_failed: int = 0,
        error_message: str | None = None,
    ) -> None:
        """Mark a run successful and persist record-movement counts."""
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
					UPDATE pipeline_runs
					SET status = 'success', finished_at = NOW(), source_url = %s,
						raw_output_path = %s, normalized_output_path = %s,
						storage_backend = %s, file_size_bytes = %s,
						records_read = %s, records_written = %s, records_failed = %s,
						error_message = %s
					WHERE id = %s
					""",
                    (
                        source_url,
                        raw_output_path,
                        normalized_output_path,
                        storage_backend,
                        file_size_bytes,
                        records_read,
                        records_written,
                        records_failed,
                        error_message[:4000] if error_message else None,
                        run_id,
                    ),
                )
                self._require_updated_row(cursor.rowcount, run_id)

    def mark_failure(
        self,
        run_id: UUID,
        error_message: str,
        records_read: int = 0,
        records_written: int = 0,
        records_failed: int = 0,
    ) -> None:
        """Mark a run failed without advancing the successful checkpoint."""
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
					UPDATE pipeline_runs
					SET status = 'failed', finished_at = NOW(), error_message = %s,
						records_read = %s, records_written = %s, records_failed = %s
					WHERE id = %s
					""",
                    (
                        error_message[:4000],
                        records_read,
                        records_written,
                        records_failed,
                        run_id,
                    ),
                )
                self._require_updated_row(cursor.rowcount, run_id)

    def last_successful_window(
        self,
        pipeline_name: str = "gdelt_events_ingestion",
        source_system: str = "GDELT",
        raw_output_path_prefix: str | None = None,
    ) -> datetime | None:
        """Return the end of the latest successful source window."""
        with self._connect() as connection:
            with connection.cursor() as cursor:
                if raw_output_path_prefix:
                    cursor.execute(
                        """
					SELECT MAX(source_window_end)
					FROM pipeline_runs
					WHERE pipeline_name = %s AND source_system = %s AND status = 'success'
						AND raw_output_path LIKE %s
					""",
                        (pipeline_name, source_system, f"{raw_output_path_prefix}%"),
                    )
                else:
                    cursor.execute(
                        """
					SELECT MAX(source_window_end)
					FROM pipeline_runs
					WHERE pipeline_name = %s AND source_system = %s AND status = 'success'
					""",
                        (pipeline_name, source_system),
                    )
                return cursor.fetchone()[0]

    def can_process_window(
        self,
        window_start: datetime,
        pipeline_name: str = "gdelt_events_ingestion",
        source_system: str = "GDELT",
        raw_output_path_prefix: str | None = None,
    ) -> bool:
        """Return whether a window is new or adjacent to the successful checkpoint."""
        last_window_end = self.last_successful_window(
            pipeline_name,
            source_system,
            raw_output_path_prefix,
        )
        return last_window_end is None or window_start >= last_window_end

    def did_finish_successfully(self, run_id: UUID) -> bool:
        """Return whether a specific pipeline run has succeeded."""
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT status = 'success' FROM pipeline_runs WHERE id = %s",
                    (run_id,),
                )
                result = cursor.fetchone()
        return bool(result and result[0])

    def _connect(self) -> Any:
        return self._connection_factory(self.database_url)

    @staticmethod
    def _require_updated_row(rowcount: int, run_id: UUID) -> None:
        if rowcount != 1:
            raise LookupError(f"Pipeline run {run_id} was not found")


def _split_sql_statements(schema_sql: str) -> list[str]:
    return [statement.strip() for statement in schema_sql.split(";") if statement.strip()]
