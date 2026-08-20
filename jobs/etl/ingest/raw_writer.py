"""Raw writer abstractions for persisting ingestion data."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol


class RawStorageWriter(Protocol):
    """Common interface for raw storage backends."""

    def write(self, content: bytes, destination_path: str) -> str:
        """Write bytes to ``destination_path`` and return the resulting path."""
        ...


class LocalRawWriter:
    """Persist raw file content to a local destination path."""

    def write(self, content: bytes, destination_path: str) -> str:
        """Write bytes to ``destination_path`` and return the resulting path."""
        path = Path(destination_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        partial_path = path.with_suffix(path.suffix + ".part")

        try:
            partial_path.write_bytes(content)
            partial_path.replace(path)
        except Exception:
            partial_path.unlink(missing_ok=True)
            raise

        return str(path)


RawWriter = LocalRawWriter
