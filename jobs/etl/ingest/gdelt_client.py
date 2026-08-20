"""Download GDELT Events export files."""

from __future__ import annotations

import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import BinaryIO
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class GDELTDownloadError(RuntimeError):
    """Raised when a GDELT Events file cannot be downloaded."""


@dataclass(frozen=True)
class DownloadMetadata:
    """Metadata for a downloaded GDELT Events file."""

    source_url: str
    file_size: int
    downloaded_at: datetime
    local_path: Path


class GDELTClient:
    """Download GDELT Events exports for a timestamp or the latest available window."""

    def __init__(
        self,
        base_url: str = "http://data.gdeltproject.org/events",
        latest_url: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.latest_url = latest_url or f"{self.base_url}/index.html"
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def download_events(
        self,
        timestamp: datetime | str = "latest",
        destination_dir: str | Path = "data/raw/gdelt/events",
    ) -> DownloadMetadata:
        """Download one Events export and return its source and local metadata."""
        timestamp_value = self._resolve_timestamp(timestamp)
        source_url = self._events_url(timestamp_value)
        destination = Path(destination_dir)
        destination.mkdir(parents=True, exist_ok=True)
        local_path = destination / Path(source_url).name
        partial_path = local_path.with_suffix(local_path.suffix + ".part")

        try:
            with self._open_with_retries(source_url) as response:
                file_size = self._write_response(response, partial_path)
            partial_path.replace(local_path)
        except Exception:
            partial_path.unlink(missing_ok=True)
            raise

        return DownloadMetadata(
            source_url=source_url,
            file_size=file_size,
            downloaded_at=datetime.now(timezone.utc),
            local_path=local_path,
        )

    def resolve_timestamp(self, timestamp: datetime | str = "latest") -> datetime:
        """Resolve a requested window to a UTC timestamp."""
        resolved = self._resolve_timestamp(timestamp)
        date_format = "%Y%m%d" if len(resolved) == 8 else "%Y%m%d%H%M%S"
        return datetime.strptime(resolved, date_format).replace(tzinfo=timezone.utc)

    def _resolve_timestamp(self, timestamp: datetime | str) -> str:
        if isinstance(timestamp, datetime):
            return timestamp.astimezone(timezone.utc).strftime("%Y%m%d%H%M%S")

        if timestamp.lower() == "latest":
            latest_text = self._read_text_with_retries(self.latest_url)
            matches = re.findall(r"(?:href=\"|\b)(\d{8}(?:\d{6})?)\.export\.CSV\.zip", latest_text)
            if not matches:
                matches = re.findall(r"\b\d{8}(?:\d{6})?\b", latest_text)
            if not matches:
                raise GDELTDownloadError(f"Could not find a GDELT timestamp in {self.latest_url}")
            return matches[0]

        for date_format in (
            "%Y%m%d%H%M%S",
            "%Y%m%d%H%M",
            "%Y%m%d",
            "%Y-%m-%dT%H:%M:%SZ",
        ):
            try:
                parsed = datetime.strptime(timestamp, date_format)
                return parsed.strftime("%Y%m%d%H%M%S")
            except ValueError:
                continue
        raise ValueError("timestamp must be 'latest', a datetime, or a supported timestamp string")

    def _events_url(self, timestamp: str) -> str:
        return f"{self.base_url}/{timestamp}.export.CSV.zip"

    def _read_text_with_retries(self, url: str) -> str:
        with self._open_with_retries(url) as response:
            return response.read().decode("utf-8")

    def _open_with_retries(self, url: str) -> BinaryIO:
        request = Request(url, headers={"User-Agent": "SignalWatch/0.1"})
        for attempt in range(self.max_retries + 1):
            try:
                return urlopen(request, timeout=self.timeout)
            except HTTPError as error:
                if not self._is_transient_status(error.code):
                    message = f"GDELT returned HTTP {error.code} for {url}"
                    raise GDELTDownloadError(message) from error
            except (TimeoutError, URLError) as error:
                if attempt == self.max_retries:
                    raise GDELTDownloadError(f"Could not download GDELT file from {url}") from error
            if attempt < self.max_retries:
                time.sleep(self.retry_delay * (2**attempt))
        raise GDELTDownloadError(f"Could not download GDELT file from {url}")

    @staticmethod
    def _is_transient_status(status_code: int) -> bool:
        return status_code in {408, 429, 500, 502, 503, 504}

    @staticmethod
    def _write_response(response: BinaryIO, partial_path: Path) -> int:
        file_size = 0
        with partial_path.open("wb") as output:
            while chunk := response.read(1024 * 1024):
                output.write(chunk)
                file_size += len(chunk)
        return file_size
