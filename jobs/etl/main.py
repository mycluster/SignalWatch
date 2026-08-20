"""Command-line entry point for the SignalWatch ETL pipeline."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from datetime import timedelta
from enum import Enum
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from jobs.etl.ingest.checkpoint_service import CheckpointService
from jobs.etl.ingest.gdelt_client import GDELTClient
from jobs.etl.ingest.raw_writer import LocalRawWriter, RawStorageWriter
from jobs.etl.load.adls_writer import AzureDataLakeRawWriter
from jobs.etl.transform.deduplicate import deduplicate_events
from jobs.etl.transform.normalize_events import normalize_gdelt_event
from jobs.etl.transform.normalized_event_writer import NormalizedEventWriter
from jobs.etl.transform.parse_gdelt_events import parse_gdelt_events_file

from signalwatch.core.config import settings

PIPELINE_NAME = "gdelt_events_ingestion"
RUN_ALL_PIPELINE_NAME = "gdelt_run_all"
SOURCE_SYSTEM = "GDELT"
RAW_ROOT = Path("bronze/gdelt/events")
SILVER_ROOT = Path("silver/normalized_events")


def ingest(
    requested_window: str,
    storage_backend: str | None = None,
    database_url: str | None = None,
    client: GDELTClient | None = None,
    checkpoint_service: CheckpointService | None = None,
    raw_writer: RawStorageWriter | None = None,
) -> int:
    """Run one GDELT Events ingestion window."""
    client = client or GDELTClient()
    checkpoint_service = checkpoint_service or CheckpointService(database_url)
    raw_writer = raw_writer or build_raw_writer(storage_backend)
    run_id = None
    window_start = None

    try:
        window_start = client.resolve_timestamp(requested_window)
        window_duration = (
            timedelta(days=1) if _is_daily_window(requested_window) else timedelta(minutes=15)
        )
        window_end = window_start + window_duration
        run_id = checkpoint_service.start_run(
            PIPELINE_NAME, SOURCE_SYSTEM, window_start, window_end
        )
        raw_output_path_prefix = _raw_output_path_prefix(raw_writer)
        if not checkpoint_service.can_process_window(
            window_start,
            PIPELINE_NAME,
            SOURCE_SYSTEM,
            raw_output_path_prefix,
        ):
            raise RuntimeError("source window is already covered by a successful run")

        with TemporaryDirectory() as temporary_directory:
            download = client.download_events(requested_window, temporary_directory)
            records_read = len(parse_gdelt_events_file(download.local_path))
            filename = download.local_path.name
            raw_path = (
                RAW_ROOT
                / f"year={window_start:%Y}"
                / f"month={window_start:%m}"
                / f"day={window_start:%d}"
                / f"hour={window_start:%H}"
                / filename
            )
            written_path = raw_writer.write(download.local_path.read_bytes(), str(raw_path))

        checkpoint_service.mark_success(
            run_id,
            source_url=download.source_url,
            raw_output_path=written_path,
            file_size_bytes=download.file_size,
            records_read=records_read,
            records_written=records_read,
            records_failed=0,
        )
    except Exception as error:
        if run_id is not None:
            checkpoint_service.mark_failure(run_id, str(error))
        print(f"Pipeline: {PIPELINE_NAME}")
        window_text = (
            window_start.isoformat().replace("+00:00", "Z") if window_start else "unresolved"
        )
        print(f"Window: {window_text}")
        print("Status: failure")
        print(f"Error: {error}")
        return 1

    print(f"Pipeline: {PIPELINE_NAME}")
    print(f"Window: {window_start.isoformat().replace('+00:00', 'Z')}")
    print("Status: success")
    print(f"Records read: {records_read}")
    print(f"Records written: {records_read}")
    print("Records failed: 0")
    print(f"Raw path: {written_path}")
    return 0


def normalize(
    raw_file: str | Path,
    database_url: str | None = None,
    checkpoint_service: CheckpointService | None = None,
    event_writer: NormalizedEventWriter | None = None,
) -> int:
    """Normalize one raw GDELT Events file."""
    raw_path = Path(raw_file)
    checkpoint_service = checkpoint_service or CheckpointService(database_url)
    event_writer = event_writer or NormalizedEventWriter(database_url)
    run_id = None
    records_read = 0
    records_written = 0
    records_failed = 0

    try:
        checkpoint_service.ensure_schema()
        event_writer.ensure_schema()
        run_id = checkpoint_service.start_run(
            "gdelt_events_normalization",
            SOURCE_SYSTEM,
        )
        parsed_rows = parse_gdelt_events_file(raw_path)
        records_read = len(parsed_rows)
        normalized_events = []
        row_errors = []
        for row_number, row in enumerate(parsed_rows, start=1):
            try:
                normalized_events.append(
                    normalize_gdelt_event(
                        row,
                        source_file_path=str(raw_path),
                        pipeline_run_id=run_id,
                    )
                )
            except Exception as error:
                records_failed += 1
                row_errors.append(f"row {row_number}: {error}")
        unique_events = deduplicate_events(normalized_events)
        records_written = event_writer.upsert_events(unique_events, pipeline_run_id=run_id)
        checkpoint_service.mark_success(
            run_id,
            raw_output_path=str(raw_path),
            records_read=records_read,
            records_written=records_written,
            records_failed=records_failed,
            error_message="; ".join(row_errors) if row_errors else None,
        )
    except Exception as error:
        if run_id:
            checkpoint_service.mark_failure(
                run_id,
                str(error),
                records_read=records_read,
                records_written=records_written,
                records_failed=records_failed,
            )
        print(f"Pipeline: {PIPELINE_NAME}")
        print(f"Raw file: {raw_path}")
        print("Status: failure")
        print(f"Error: {error}")
        return 1

    print(f"Pipeline: {PIPELINE_NAME}")
    print(f"Raw file: {raw_path}")
    print("Status: success")
    print(f"Records read: {len(parsed_rows)}")
    print(f"Records written: {records_written}")
    print(f"Records failed: {records_failed}")
    print(f"Records normalized: {len(normalized_events)}")
    print(f"Records after deduplication: {records_written}")
    if unique_events:
        sample = asdict(unique_events[0])
        print(f"Sample event id: {sample['id']}")
        print(f"Sample source event id: {sample['source_event_id']}")
    return 0


def run_all(
    requested_window: str,
    storage_backend: str | None = None,
    database_url: str | None = None,
    client: GDELTClient | None = None,
    checkpoint_service: CheckpointService | None = None,
    raw_writer: RawStorageWriter | None = None,
    silver_writer: RawStorageWriter | None = None,
    event_writer: NormalizedEventWriter | None = None,
) -> int:
    """Download, bronze-write, normalize, persist, silver-write, and checkpoint one window."""
    backend = (storage_backend or settings.storage_backend).lower()
    client = client or GDELTClient()
    checkpoint_service = checkpoint_service or CheckpointService(database_url)
    raw_writer = raw_writer or build_raw_writer(backend)
    silver_writer = silver_writer or build_raw_writer(backend)
    event_writer = event_writer or NormalizedEventWriter(database_url)
    run_id = None
    window_start = None
    records_read = 0
    records_normalized = 0
    records_failed = 0
    records_written_to_postgres = 0
    records_written_to_silver = 0
    bronze_path = None
    silver_path = None

    try:
        checkpoint_service.ensure_schema()
        event_writer.ensure_schema()
        window_start = client.resolve_timestamp(requested_window)
        window_duration = (
            timedelta(days=1) if _is_daily_window(requested_window) else timedelta(minutes=15)
        )
        window_end = window_start + window_duration
        run_id = checkpoint_service.start_run(
            RUN_ALL_PIPELINE_NAME, SOURCE_SYSTEM, window_start, window_end
        )
        raw_output_path_prefix = _raw_output_path_prefix(raw_writer)
        if not checkpoint_service.can_process_window(
            window_start,
            RUN_ALL_PIPELINE_NAME,
            SOURCE_SYSTEM,
            raw_output_path_prefix,
        ):
            raise RuntimeError("source window is already covered by a successful run")

        with TemporaryDirectory() as temporary_directory:
            download = client.download_events(requested_window, temporary_directory)
            filename = download.local_path.name
            source_timestamp = _source_timestamp_from_filename(filename)
            bronze_destination = _bronze_path(window_start, filename)
            bronze_path = raw_writer.write(
                download.local_path.read_bytes(),
                str(bronze_destination),
            )

            parsed_rows = parse_gdelt_events_file(download.local_path)
            records_read = len(parsed_rows)
            normalized_events = []
            row_errors = []
            for row_number, row in enumerate(parsed_rows, start=1):
                try:
                    normalized_events.append(
                        normalize_gdelt_event(
                            row,
                            source_file_path=bronze_path,
                            pipeline_run_id=run_id,
                        )
                    )
                except Exception as error:
                    records_failed += 1
                    row_errors.append(f"row {row_number}: {error}")

            unique_events = deduplicate_events(normalized_events)
            records_normalized = len(unique_events)
            records_written_to_postgres = event_writer.upsert_events(
                unique_events,
                pipeline_run_id=run_id,
            )
            silver_destination = _silver_path(window_start, source_timestamp)
            silver_path = silver_writer.write(
                _events_to_jsonl(unique_events),
                str(silver_destination),
            )
            records_written_to_silver = len(unique_events)

        checkpoint_service.mark_success(
            run_id,
            source_url=download.source_url,
            raw_output_path=bronze_path,
            normalized_output_path=silver_path,
            storage_backend=backend,
            file_size_bytes=download.file_size,
            records_read=records_read,
            records_written=records_written_to_postgres,
            records_failed=records_failed,
            error_message="; ".join(row_errors) if row_errors else None,
        )
    except Exception as error:
        if run_id is not None:
            checkpoint_service.mark_failure(
                run_id,
                str(error),
                records_read=records_read,
                records_written=records_written_to_postgres,
                records_failed=records_failed,
            )
        print(f"Pipeline: {RUN_ALL_PIPELINE_NAME}")
        print("Status: failure")
        print(f"Storage backend: {backend}")
        if bronze_path:
            print(f"Bronze path: {bronze_path}")
        if silver_path:
            print(f"Silver path: {silver_path}")
        print(f"Error: {error}")
        return 1

    print(f"Pipeline: {RUN_ALL_PIPELINE_NAME}")
    print("Status: success")
    print(f"Storage backend: {backend}")
    print(f"Bronze path: {bronze_path}")
    print(f"Silver path: {silver_path}")
    print(f"Records read: {records_read}")
    print(f"Records normalized: {records_normalized}")
    print(f"Records written to Postgres: {records_written_to_postgres}")
    print(f"Records written to ADLS silver: {records_written_to_silver}")
    return 0


def _is_daily_window(requested_window: str) -> bool:
    return requested_window.lower() == "latest" or len(requested_window) == 8


def _bronze_path(window_start, filename: str) -> Path:
    return (
        RAW_ROOT
        / f"year={window_start:%Y}"
        / f"month={window_start:%m}"
        / f"day={window_start:%d}"
        / f"hour={window_start:%H}"
        / filename
    )


def _silver_path(window_start, source_timestamp: str) -> Path:
    return (
        SILVER_ROOT
        / f"year={window_start:%Y}"
        / f"month={window_start:%m}"
        / f"day={window_start:%d}"
        / f"normalized-events-{source_timestamp}.jsonl"
    )


def _source_timestamp_from_filename(filename: str) -> str:
    return filename.split(".export", maxsplit=1)[0]


def _events_to_jsonl(events) -> bytes:
    lines = [json.dumps(asdict(event), default=_json_default, sort_keys=True) for event in events]
    return ("\n".join(lines) + ("\n" if lines else "")).encode("utf-8")


def _json_default(value: Any) -> str:
    if isinstance(value, Enum):
        return value.value
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def _raw_output_path_prefix(raw_writer: RawStorageWriter) -> str | None:
    if isinstance(raw_writer, AzureDataLakeRawWriter):
        return "abfss://"
    if isinstance(raw_writer, LocalRawWriter):
        return str(RAW_ROOT)
    return None


def build_raw_writer(storage_backend: str | None = None) -> RawStorageWriter:
    """Return the configured raw storage backend."""
    backend = (storage_backend or settings.storage_backend).lower()
    if backend == "local":
        return LocalRawWriter()
    if backend == "azure":
        return AzureDataLakeRawWriter(
            account_name=settings.azure_storage_account_name,
            container_name=settings.azure_storage_container_name,
        )
    raise ValueError("STORAGE_BACKEND must be 'local' or 'azure'")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run SignalWatch ETL ingestion")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest_parser = subparsers.add_parser("ingest", help="Ingest one GDELT Events file")
    ingest_parser.add_argument("--window", choices=("latest",), default="latest")
    ingest_parser.add_argument("--timestamp", help="GDELT timestamp, e.g. 20260819231500")
    ingest_parser.add_argument("--storage", choices=("local", "azure"), help="Raw storage backend")
    ingest_parser.add_argument("--database-url", help="Postgres connection URL")

    run_all_parser = subparsers.add_parser(
        "run-all", help="Run GDELT ingestion, normalization, Postgres load, and silver write"
    )
    run_all_parser.add_argument("--window", choices=("latest",), default="latest")
    run_all_parser.add_argument("--timestamp", help="GDELT timestamp, e.g. 20260819231500")
    run_all_parser.add_argument("--storage", choices=("local", "azure"), help="Storage backend")
    run_all_parser.add_argument("--database-url", help="Postgres connection URL")

    normalize_parser = subparsers.add_parser(
        "normalize", help="Normalize one raw GDELT Events file"
    )
    normalize_parser.add_argument(
        "--raw-file", required=True, help="Path to a raw GDELT CSV or CSV zip"
    )
    normalize_parser.add_argument("--database-url", help="Postgres connection URL")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "ingest":
        requested_window = args.timestamp or args.window
        return ingest(requested_window, args.storage, args.database_url)
    if args.command == "run-all":
        requested_window = args.timestamp or args.window
        return run_all(requested_window, args.storage, args.database_url)
    if args.command == "normalize":
        return normalize(args.raw_file, args.database_url)
    return 2


if __name__ == "__main__":
    sys.exit(main())
