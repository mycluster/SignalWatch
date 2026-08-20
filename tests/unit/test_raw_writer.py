"""Tests for the local raw writer."""

from pathlib import Path

from jobs.etl.ingest.raw_writer import RawWriter


def test_write_creates_partitioned_event_path(tmp_path) -> None:
    destination = (
        tmp_path
        / "data"
        / "raw"
        / "gdelt"
        / "events"
        / "year=2026"
        / "month=08"
        / "day=19"
        / "hour=23"
        / "events.csv.zip"
    )

    written_path = RawWriter().write(b"raw events", str(destination))

    assert Path(written_path) == destination
    assert destination.read_bytes() == b"raw events"
    assert not destination.with_suffix(destination.suffix + ".part").exists()


def test_write_replaces_existing_file(tmp_path) -> None:
    destination = tmp_path / "events.csv.zip"
    destination.write_bytes(b"old content")

    RawWriter().write(b"new content", str(destination))

    assert destination.read_bytes() == b"new content"
