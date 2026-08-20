"""Tests for GDELT event-category mapping."""

from jobs.etl.transform.event_category_mapper import map_event_category
from packages.signalwatch_common.enums import EventCategory


def test_maps_known_root_code_to_category() -> None:
    assert map_event_category("14") == EventCategory.PROTEST


def test_maps_conflict_root_codes_to_conflict() -> None:
    assert map_event_category("18") == EventCategory.CONFLICT
    assert map_event_category("19") == EventCategory.CONFLICT
    assert map_event_category("20") == EventCategory.CONFLICT


def test_maps_labor_event_codes_before_root_code() -> None:
    assert map_event_category("14", "143") == EventCategory.LABOR_ACTION
    assert map_event_category("14", "1432") == EventCategory.LABOR_ACTION


def test_maps_transport_disruption_event_codes() -> None:
    assert map_event_category("17", "172") == EventCategory.TRANSPORT_DISRUPTION


def test_maps_unhandled_root_code_to_other() -> None:
    assert map_event_category("01") == EventCategory.OTHER


def test_maps_missing_root_code_to_unknown() -> None:
    assert map_event_category("") == EventCategory.UNKNOWN
