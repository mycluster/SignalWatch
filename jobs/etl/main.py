"""Command-line entry point for the SignalWatch ETL pipeline."""

from __future__ import annotations

import argparse
import sys
from datetime import timedelta
from pathlib import Path
from tempfile import TemporaryDirectory

from jobs.etl.ingest.checkpoint_service import CheckpointService
from jobs.etl.ingest.gdelt_client import GDELTClient
from jobs.etl.ingest.raw_writer import RawWriter

PIPELINE_NAME = "gdelt_events_ingestion"
SOURCE_SYSTEM = "GDELT"
RAW_ROOT = Path("data/raw/gdelt/events")


def ingest(
    requested_window: str,
    database_url: str | None = None,
    client: GDELTClient | None = None,
    checkpoint_service: CheckpointService | None = None,
    raw_writer: RawWriter | None = None,
) -> int:
    """Run one GDELT Events ingestion window."""
    client = client or GDELTClient()
    checkpoint_service = checkpoint_service or CheckpointService(database_url)
    raw_writer = raw_writer or RawWriter()
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
        if not checkpoint_service.can_process_window(window_start, PIPELINE_NAME, SOURCE_SYSTEM):
            raise RuntimeError("source window is already covered by a successful run")

        with TemporaryDirectory() as temporary_directory:
            download = client.download_events(requested_window, temporary_directory)
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
            run_id, download.source_url, written_path, download.file_size
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
    print("Records read: pending normalization")
    print(f"Raw path: {written_path}")
    return 0


def _is_daily_window(requested_window: str) -> bool:
    return requested_window.lower() == "latest" or len(requested_window) == 8


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run SignalWatch ETL ingestion")
    subparsers = parser.add_subparsers(dest="command", required=True)
    ingest_parser = subparsers.add_parser("ingest", help="Ingest one GDELT Events file")
    ingest_parser.add_argument("--window", choices=("latest",), default="latest")
    ingest_parser.add_argument("--timestamp", help="GDELT timestamp, e.g. 20260819231500")
    ingest_parser.add_argument("--database-url", help="Postgres connection URL")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "ingest":
        requested_window = args.timestamp or args.window
        return ingest(requested_window, args.database_url)
    return 2


if __name__ == "__main__":
    sys.exit(main())
