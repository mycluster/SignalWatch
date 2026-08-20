"""Map GDELT event codes into SignalWatch categories."""

from __future__ import annotations

from packages.signalwatch_common.enums import EventCategory

_LABOR_ACTION_EVENT_CODE_PREFIXES = ("143",)
_TRANSPORT_DISRUPTION_EVENT_CODE_PREFIXES = ("172",)

_ROOT_CODE_TO_CATEGORY = {
    "09": EventCategory.GOVERNMENT_ACTION,
    "10": EventCategory.GOVERNMENT_ACTION,
    "11": EventCategory.GOVERNMENT_ACTION,
    "12": EventCategory.GOVERNMENT_ACTION,
    "14": EventCategory.PROTEST,
    "18": EventCategory.CONFLICT,
    "19": EventCategory.CONFLICT,
    "20": EventCategory.CONFLICT,
}


def map_event_category(
    event_root_code: str | None,
    event_code: str | None = None,
) -> EventCategory:
    """Return a SignalWatch category for GDELT CAMEO event codes."""
    normalized_event_code = _normalize_code(event_code)
    if _has_prefix(normalized_event_code, _LABOR_ACTION_EVENT_CODE_PREFIXES):
        return EventCategory.LABOR_ACTION
    if _has_prefix(normalized_event_code, _TRANSPORT_DISRUPTION_EVENT_CODE_PREFIXES):
        return EventCategory.TRANSPORT_DISRUPTION

    normalized_root_code = _normalize_code(event_root_code)
    if not normalized_root_code:
        return EventCategory.UNKNOWN
    return _ROOT_CODE_TO_CATEGORY.get(normalized_root_code.zfill(2), EventCategory.OTHER)


def _normalize_code(code: str | None) -> str:
    return (code or "").strip()


def _has_prefix(code: str, prefixes: tuple[str, ...]) -> bool:
    return any(code.startswith(prefix) for prefix in prefixes)
