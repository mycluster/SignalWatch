"""Schemas for pipeline observability API responses."""
# ruff: noqa: UP045

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PipelineHealthResponse(BaseModel):
    """Latest pipeline health status."""

    status: str
    latest_pipeline: Optional[str] = None
    latest_successful_run: Optional[datetime] = None
    records_read: int = 0
    records_written: int = 0
    records_failed: int = 0
