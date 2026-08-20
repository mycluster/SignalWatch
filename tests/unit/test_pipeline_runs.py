"""Tests for checkpoint and ingestion-run behavior."""

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from zipfile import ZipFile

from jobs.etl.ingest.checkpoint_service import CheckpointService
from jobs.etl.ingest.gdelt_client import DownloadMetadata
from jobs.etl.main import ingest, main, run_all
from jobs.etl.transform.parse_gdelt_events import GDELT_EVENT_FIELDS


class FakeCursor:
    rowcount = 1

    def __init__(self, result=None) -> None:
        self.result = result
        self.statements = []

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return None

    def execute(self, statement, parameters=None) -> None:
        self.statements.append((statement, parameters))

    def fetchone(self):
        return self.result


class FakeConnection:
    def __init__(self, cursor) -> None:
        self.fake_cursor = cursor

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return None

    def cursor(self):
        return self.fake_cursor


def test_last_successful_window_reads_successful_checkpoint() -> None:
    expected_window = datetime(2026, 8, 19, 23, 15, tzinfo=timezone.utc)
    cursor = FakeCursor((expected_window,))
    service = CheckpointService(connection_factory=lambda _: FakeConnection(cursor))

    assert service.last_successful_window() == expected_window
    assert "status = 'success'" in cursor.statements[0][0]


def test_last_successful_window_can_filter_by_raw_output_path_prefix() -> None:
    expected_window = datetime(2026, 8, 19, 23, 15, tzinfo=timezone.utc)
    cursor = FakeCursor((expected_window,))
    service = CheckpointService(connection_factory=lambda _: FakeConnection(cursor))

    result = service.last_successful_window(raw_output_path_prefix="abfss://")

    statement, parameters = cursor.statements[0]
    assert result == expected_window
    assert "raw_output_path LIKE %s" in statement
    assert parameters[-1] == "abfss://%"


class FakeClient:
    def resolve_timestamp(self, requested_window):
        return datetime(2026, 8, 19, 23, 15, tzinfo=timezone.utc)

    def download_events(self, timestamp, destination_dir):
        path = Path(destination_dir) / "20260819231500.export.CSV.zip"
        row = [""] * len(GDELT_EVENT_FIELDS)
        row[0] = "123"
        row[1] = "20260819"
        with ZipFile(path, "w") as archive:
            archive.writestr("20260819231500.export.CSV", "\t".join(row))
        return DownloadMetadata(
            source_url="https://example.test/events/20260819231500.export.CSV.zip",
            file_size=path.stat().st_size,
            downloaded_at=datetime.now(timezone.utc),
            local_path=path,
        )


class FakeCheckpoint:
    def __init__(self) -> None:
        self.run_id = uuid4()
        self.events = []
        self.success_kwargs = None
        self.failure_kwargs = None

    def start_run(self, *args):
        self.events.append("start")
        return self.run_id

    def ensure_schema(self):
        self.events.append("ensure_checkpoint_schema")

    def can_process_window(self, *args):
        return True

    def mark_success(self, *args, **kwargs):
        self.events.append("success")
        self.success_kwargs = kwargs

    def mark_failure(self, *args, **kwargs):
        self.events.append("failure")
        self.failure_kwargs = kwargs


class FakeWriter:
    def __init__(self) -> None:
        self.writes = []

    def write(self, content, destination_path):
        Path(destination_path).parent.mkdir(parents=True, exist_ok=True)
        Path(destination_path).write_bytes(content)
        self.writes.append((content, destination_path))
        return destination_path


class FakeEventWriter:
    def __init__(self) -> None:
        self.events = []
        self.persisted_events = []
        self.pipeline_run_id = None

    def ensure_schema(self):
        self.events.append("ensure_event_schema")

    def upsert_events(self, events, pipeline_run_id=None):
        self.persisted_events = list(events)
        self.pipeline_run_id = pipeline_run_id
        return len(self.persisted_events)


def test_ingest_marks_success_only_after_raw_write(tmp_path, monkeypatch, capsys) -> None:
    checkpoint = FakeCheckpoint()
    monkeypatch.setattr("jobs.etl.main.RAW_ROOT", tmp_path / "data/raw/gdelt/events")

    result = ingest(
        "latest",
        client=FakeClient(),
        checkpoint_service=checkpoint,
        raw_writer=FakeWriter(),
    )

    assert result == 0
    assert checkpoint.events == ["start", "success"]
    assert checkpoint.success_kwargs["records_read"] == 1
    assert checkpoint.success_kwargs["records_written"] == 1
    assert checkpoint.success_kwargs["records_failed"] == 0
    output = capsys.readouterr().out
    assert "Status: success" in output
    assert "Records read: 1" in output
    assert "Records written: 1" in output
    assert "Records failed: 0" in output


def test_run_all_writes_bronze_postgres_silver_and_checkpoint(
    tmp_path, monkeypatch, capsys
) -> None:
    checkpoint = FakeCheckpoint()
    writer = FakeWriter()
    event_writer = FakeEventWriter()
    monkeypatch.setattr("jobs.etl.main.RAW_ROOT", tmp_path / "bronze/gdelt/events")
    monkeypatch.setattr("jobs.etl.main.SILVER_ROOT", tmp_path / "silver/normalized_events")

    result = run_all(
        "latest",
        storage_backend="local",
        client=FakeClient(),
        checkpoint_service=checkpoint,
        raw_writer=writer,
        silver_writer=writer,
        event_writer=event_writer,
    )

    output = capsys.readouterr().out
    assert result == 0
    assert checkpoint.events == ["ensure_checkpoint_schema", "start", "success"]
    assert event_writer.events == ["ensure_event_schema"]
    assert len(event_writer.persisted_events) == 1
    assert len(writer.writes) == 2
    assert "bronze/gdelt/events" in writer.writes[0][1].replace("\\", "/")
    assert "silver/normalized_events" in writer.writes[1][1].replace("\\", "/")
    assert writer.writes[1][0].endswith(b"\n")
    assert checkpoint.success_kwargs["raw_output_path"]
    assert checkpoint.success_kwargs["normalized_output_path"]
    assert checkpoint.success_kwargs["storage_backend"] == "local"
    assert checkpoint.success_kwargs["records_read"] == 1
    assert checkpoint.success_kwargs["records_written"] == 1
    assert "Pipeline: gdelt_run_all" in output
    assert "Records written to Postgres: 1" in output
    assert "Records written to ADLS silver: 1" in output


def test_normalize_command_reads_raw_zip(tmp_path, capsys, monkeypatch) -> None:
    checkpoint = FakeCheckpoint()
    event_writer = FakeEventWriter()
    monkeypatch.setattr("jobs.etl.main.CheckpointService", lambda *_: checkpoint)
    monkeypatch.setattr("jobs.etl.main.NormalizedEventWriter", lambda *_: event_writer)
    row = [""] * len(GDELT_EVENT_FIELDS)
    row[0] = "123"
    row[1] = "20260820"
    row[6] = "PORT WORKERS"
    row[26] = "141"
    row[28] = "14"
    row[56] = "20260820123000"
    raw_zip = tmp_path / "20260820000000.export.CSV.zip"

    with ZipFile(raw_zip, "w") as archive:
        archive.writestr("20260820000000.export.CSV", "\t".join(row))

    result = main(["normalize", "--raw-file", str(raw_zip)])

    output = capsys.readouterr().out
    assert result == 0
    assert "Status: success" in output
    assert "Records read: 1" in output
    assert "Records written: 1" in output
    assert "Records failed: 0" in output
    assert "Records after deduplication: 1" in output
    assert checkpoint.events == ["ensure_checkpoint_schema", "start", "success"]
    assert event_writer.events == ["ensure_event_schema"]
    assert event_writer.pipeline_run_id == checkpoint.run_id


def test_normalize_command_counts_row_failures_without_failing_run(
    tmp_path, capsys, monkeypatch
) -> None:
    checkpoint = FakeCheckpoint()
    event_writer = FakeEventWriter()
    monkeypatch.setattr("jobs.etl.main.CheckpointService", lambda *_: checkpoint)
    monkeypatch.setattr("jobs.etl.main.NormalizedEventWriter", lambda *_: event_writer)
    good_row = [""] * len(GDELT_EVENT_FIELDS)
    good_row[0] = "123"
    good_row[1] = "20260820"
    bad_row = [""] * len(GDELT_EVENT_FIELDS)
    bad_row[0] = "456"
    bad_row[1] = "not-a-date"
    raw_zip = tmp_path / "20260820000000.export.CSV.zip"

    with ZipFile(raw_zip, "w") as archive:
        archive.writestr(
            "20260820000000.export.CSV",
            "\n".join(("\t".join(good_row), "\t".join(bad_row))),
        )

    result = main(["normalize", "--raw-file", str(raw_zip)])

    output = capsys.readouterr().out
    assert result == 0
    assert "Status: success" in output
    assert "Records read: 2" in output
    assert "Records written: 1" in output
    assert "Records failed: 1" in output
    assert checkpoint.success_kwargs["records_read"] == 2
    assert checkpoint.success_kwargs["records_written"] == 1
    assert checkpoint.success_kwargs["records_failed"] == 1


def test_checkpoint_success_updates_record_movement_fields() -> None:
    cursor = FakeCursor()
    run_id = uuid4()
    service = CheckpointService(connection_factory=lambda _: FakeConnection(cursor))

    service.mark_success(
        run_id,
        records_read=2845,
        records_written=2810,
        records_failed=35,
    )

    statement, parameters = cursor.statements[0]
    assert "records_read = %s" in statement
    assert "records_written = %s" in statement
    assert "records_failed = %s" in statement
    assert 2845 in parameters
    assert 2810 in parameters
    assert 35 in parameters


def test_checkpoint_success_updates_storage_lineage_fields() -> None:
    cursor = FakeCursor()
    run_id = uuid4()
    service = CheckpointService(connection_factory=lambda _: FakeConnection(cursor))

    service.mark_success(
        run_id,
        raw_output_path="abfss://bronze",
        normalized_output_path="abfss://silver",
        storage_backend="azure",
    )

    statement, parameters = cursor.statements[0]
    assert "normalized_output_path = %s" in statement
    assert "storage_backend = %s" in statement
    assert "abfss://bronze" in parameters
    assert "abfss://silver" in parameters
    assert "azure" in parameters


def test_checkpoint_failure_updates_status_counts_and_error() -> None:
    cursor = FakeCursor()
    run_id = uuid4()
    service = CheckpointService(connection_factory=lambda _: FakeConnection(cursor))

    service.mark_failure(
        run_id,
        "corrupt file",
        records_read=10,
        records_written=8,
        records_failed=2,
    )

    statement, parameters = cursor.statements[0]
    assert "status = 'failed'" in statement
    assert "finished_at = NOW()" in statement
    assert "error_message = %s" in statement
    assert parameters == ("corrupt file", 10, 8, 2, run_id)
