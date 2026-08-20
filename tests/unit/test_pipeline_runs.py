"""Tests for checkpoint and ingestion-run behavior."""

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from jobs.etl.ingest.checkpoint_service import CheckpointService
from jobs.etl.ingest.gdelt_client import DownloadMetadata
from jobs.etl.main import ingest


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


class FakeClient:
	def resolve_timestamp(self, requested_window):
		return datetime(2026, 8, 19, 23, 15, tzinfo=timezone.utc)

	def download_events(self, timestamp, destination_dir):
		path = Path(destination_dir) / "20260819231500.export.CSV.zip"
		path.write_bytes(b"events")
		return DownloadMetadata(
			source_url="https://example.test/events/20260819231500.export.CSV.zip",
			file_size=6,
			downloaded_at=datetime.now(timezone.utc),
			local_path=path,
		)


class FakeCheckpoint:
	def __init__(self) -> None:
		self.run_id = uuid4()
		self.events = []

	def start_run(self, *args):
		self.events.append("start")
		return self.run_id

	def can_process_window(self, *args):
		return True

	def mark_success(self, *args):
		self.events.append("success")

	def mark_failure(self, *args):
		self.events.append("failure")


class FakeWriter:
	def write(self, content, destination_path):
		assert content == b"events"
		Path(destination_path).parent.mkdir(parents=True, exist_ok=True)
		Path(destination_path).write_bytes(content)
		return destination_path


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
	assert "Status: success" in capsys.readouterr().out
