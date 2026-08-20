"""Deduplicate normalized event records."""

from __future__ import annotations

from collections.abc import Iterable

from packages.signalwatch_common.models.normalized_event import NormalizedEvent


def deduplicate_events(events: Iterable[NormalizedEvent]) -> list[NormalizedEvent]:
    """Keep the first event for each source system/event id pair."""
    seen: set[tuple[str, str]] = set()
    unique_events: list[NormalizedEvent] = []

    for event in events:
        key = (event.source_system, event.source_event_id)
        if key in seen:
            continue
        seen.add(key)
        unique_events.append(event)

    return unique_events
