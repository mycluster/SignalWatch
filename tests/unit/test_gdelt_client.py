"""Tests for the GDELT Events client."""

from io import BytesIO
from unittest.mock import patch
from urllib.error import HTTPError

import pytest
from jobs.etl.ingest.gdelt_client import GDELTClient, GDELTDownloadError


class FakeResponse(BytesIO):
    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


def test_download_events_builds_timestamped_url_and_returns_metadata(tmp_path) -> None:
    response = FakeResponse(b"events")
    client = GDELTClient(base_url="https://example.test/events", retry_delay=0)

    with patch("jobs.etl.ingest.gdelt_client.urlopen", return_value=response) as open_url:
        metadata = client.download_events("20260819123000", tmp_path)

    assert metadata.source_url == ("https://example.test/events/20260819123000.export.CSV.zip")
    assert metadata.file_size == 6
    assert metadata.downloaded_at.tzinfo is not None
    assert metadata.local_path.read_bytes() == b"events"
    open_url.assert_called_once()


def test_latest_resolves_timestamp_and_retries_transient_http_failure(tmp_path) -> None:
    latest_response = FakeResponse(b"20260819124500.export.CSV.zip\n")
    events_response = FakeResponse(b"latest-events")
    responses = [HTTPError("url", 503, "busy", {}, None), latest_response, events_response]
    client = GDELTClient(base_url="https://example.test/events", retry_delay=0)

    with patch("jobs.etl.ingest.gdelt_client.urlopen", side_effect=responses) as open_url:
        metadata = client.download_events("latest", tmp_path)

    assert metadata.source_url.endswith("20260819124500.export.CSV.zip")
    assert metadata.local_path.read_bytes() == b"latest-events"
    assert open_url.call_count == 3


def test_permanent_http_failure_raises_download_error(tmp_path) -> None:
    failure = HTTPError("url", 404, "missing", {}, None)
    client = GDELTClient(base_url="https://example.test/events", retry_delay=0)

    with patch("jobs.etl.ingest.gdelt_client.urlopen", side_effect=failure):
        with pytest.raises(GDELTDownloadError, match="HTTP 404"):
            client.download_events("20260819123000", tmp_path)
