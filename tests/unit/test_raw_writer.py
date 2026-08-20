"""Tests for the local raw writer."""

from pathlib import Path

from jobs.etl.ingest.raw_writer import LocalRawWriter, RawWriter
from jobs.etl.load.adls_writer import AzureDataLakeRawWriter
from jobs.etl.main import build_raw_writer


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


def test_build_raw_writer_uses_local_backend() -> None:
    assert isinstance(build_raw_writer("local"), LocalRawWriter)


def test_build_raw_writer_rejects_unknown_backend() -> None:
    try:
        build_raw_writer("unknown")
    except ValueError as error:
        assert "STORAGE_BACKEND" in str(error)
    else:
        raise AssertionError("Expected ValueError for unknown storage backend")


def test_build_raw_writer_uses_azure_backend(monkeypatch) -> None:
    captured = {}

    class FakeAzureWriter:
        def __init__(self, account_name, container_name) -> None:
            captured["account_name"] = account_name
            captured["container_name"] = container_name

    monkeypatch.setattr("jobs.etl.main.AzureDataLakeRawWriter", FakeAzureWriter)
    monkeypatch.setattr("jobs.etl.main.settings.azure_storage_account_name", "acct")
    monkeypatch.setattr("jobs.etl.main.settings.azure_storage_container_name", "signalwatch")

    writer = build_raw_writer("azure")

    assert isinstance(writer, FakeAzureWriter)
    assert captured == {
        "account_name": "acct",
        "container_name": "signalwatch",
    }


class FakeFileClient:
    def __init__(self) -> None:
        self.uploaded_content = None
        self.overwrite = None

    def upload_data(self, content, overwrite=False) -> None:
        self.uploaded_content = content
        self.overwrite = overwrite


class FakeFileSystemClient:
    def __init__(self, file_client) -> None:
        self.file_client = file_client
        self.path = None

    def get_file_client(self, path):
        self.path = path
        return self.file_client


class FakeDataLakeServiceClient:
    def __init__(self, file_system_client) -> None:
        self.file_system_client = file_system_client
        self.container_name = None

    def get_file_system_client(self, container_name):
        self.container_name = container_name
        return self.file_system_client


def test_azure_data_lake_writer_uploads_raw_content() -> None:
    file_client = FakeFileClient()
    file_system_client = FakeFileSystemClient(file_client)
    service_client = FakeDataLakeServiceClient(file_system_client)
    writer = AzureDataLakeRawWriter(
        account_name="acct",
        container_name="signalwatch",
        service_client=service_client,
    )

    written_path = writer.write(
        b"raw events",
        "data\\raw\\gdelt\\events\\year=2026\\events.CSV.zip",
    )

    assert service_client.container_name == "signalwatch"
    assert file_system_client.path == "data/raw/gdelt/events/year=2026/events.CSV.zip"
    assert file_client.uploaded_content == b"raw events"
    assert file_client.overwrite is True
    assert (
        written_path == "abfss://signalwatch@acct.dfs.core.windows.net/"
        "data/raw/gdelt/events/year=2026/events.CSV.zip"
    )
