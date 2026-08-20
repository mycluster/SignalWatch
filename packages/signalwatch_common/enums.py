"""Shared enums used across SignalWatch jobs and services."""

from __future__ import annotations

from enum import Enum


class EventCategory(str, Enum):
    """High-level SignalWatch event categories."""

    PROTEST = "PROTEST"
    LABOR_ACTION = "LABOR_ACTION"
    TRANSPORT_DISRUPTION = "TRANSPORT_DISRUPTION"
    CONFLICT = "CONFLICT"
    GOVERNMENT_ACTION = "GOVERNMENT_ACTION"
    OTHER = "OTHER"
    UNKNOWN = "UNKNOWN"


class Domain(str, Enum):
    """Signal domains used by normalized events."""

    GENERAL = "GENERAL"
    SUPPLY_CHAIN = "SUPPLY_CHAIN"
