"""Normalize parsed GDELT rows into SignalWatch event records."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from uuid import UUID

from jobs.etl.transform.event_category_mapper import map_event_category
from packages.signalwatch_common.enums import Domain, EventCategory
from packages.signalwatch_common.models.normalized_event import NormalizedEvent

SUPPLY_CHAIN_CATEGORY_SCORE = 70.0
SUPPLY_CHAIN_KEYWORD_SCORE = 20.0
SUPPLY_CHAIN_CONFIDENCE_SCORE = 60.0
DEFAULT_CONFIDENCE_SCORE = 30.0

SUPPLY_CHAIN_LOCATION_TERMS = (
    "border",
    "fuel",
    "logistics",
    "port",
    "rail",
    "shipping",
)
SUPPLY_CHAIN_ACTOR_TERMS = (
    "dock",
    "port",
    "railway",
    "transport",
    "truck",
    "union",
)
SUPPLY_CHAIN_CATEGORIES = (
    EventCategory.LABOR_ACTION,
    EventCategory.TRANSPORT_DISRUPTION,
)

SUPPLY_CHAIN_TERMS = (
    *SUPPLY_CHAIN_LOCATION_TERMS,
    *SUPPLY_CHAIN_ACTOR_TERMS,
    "transport",
)

GDELT_TO_NORMALIZED_FIELDS = {
    "GLOBALEVENTID": "source_event_id",
    "SQLDATE": "event_date",
    "Actor1Name": "actor_1_name",
    "Actor1CountryCode": "actor_1_country_code",
    "Actor1Type1Code": "actor_1_type",
    "Actor2Name": "actor_2_name",
    "Actor2CountryCode": "actor_2_country_code",
    "Actor2Type1Code": "actor_2_type",
    "EventCode": "event_code",
    "EventRootCode": "event_root_code",
    "GoldsteinScale": "goldstein_score",
    "AvgTone": "avg_tone",
    "NumMentions": "mention_count",
    "NumSources": "source_count",
    "NumArticles": "article_count",
    "ActionGeo_CountryCode": "country_code",
    "ActionGeo_FullName": "city",
    "ActionGeo_Lat": "latitude",
    "ActionGeo_Long": "longitude",
    "SOURCEURL": "source_url",
}

_FIELD_ALIASES = {
    "GLOBALEVENTID": "global_event_id",
    "SQLDATE": "day",
    "Actor1Name": "actor_1_name",
    "Actor1CountryCode": "actor_1_country_code",
    "Actor1Type1Code": "actor_1_type_1_code",
    "Actor2Name": "actor_2_name",
    "Actor2CountryCode": "actor_2_country_code",
    "Actor2Type1Code": "actor_2_type_1_code",
    "EventCode": "event_code",
    "EventRootCode": "event_root_code",
    "GoldsteinScale": "goldstein_scale",
    "AvgTone": "avg_tone",
    "NumMentions": "num_mentions",
    "NumSources": "num_sources",
    "NumArticles": "num_articles",
    "ActionGeo_Type": "action_geo_type",
    "ActionGeo_FullName": "action_geo_fullname",
    "ActionGeo_CountryCode": "action_geo_country_code",
    "ActionGeo_ADM1Code": "action_geo_adm1_code",
    "ActionGeo_Lat": "action_geo_lat",
    "ActionGeo_Long": "action_geo_long",
    "DATEADDED": "date_added",
    "SOURCEURL": "source_url",
}


def normalize_gdelt_event(
    row: dict[str, str],
    source_file_path: str | None = None,
    pipeline_run_id: UUID | None = None,
) -> NormalizedEvent:
    """Convert one parsed GDELT event row into the shared normalized model."""
    normalized_at = datetime.now(timezone.utc)
    event_code = _empty_to_none(_value(row, "EventCode"))
    root_code = _empty_to_none(_value(row, "EventRootCode"))
    category = map_event_category(root_code, event_code)
    source_event_id = _value(row, "GLOBALEVENTID") or _stable_hash(row)
    source_url = _empty_to_none(_value(row, "SOURCEURL"))
    location_text = _empty_to_none(_value(row, "ActionGeo_FullName"))
    actor_1_name = _empty_to_none(_value(row, "Actor1Name"))
    actor_2_name = _empty_to_none(_value(row, "Actor2Name"))
    relevance_score = _supply_chain_relevance_score(
        category=category,
        source_url=source_url,
        location_text=location_text,
        actor_names=(actor_1_name, actor_2_name),
    )
    is_supply_chain_related = relevance_score > 0

    return NormalizedEvent(
        source_event_id=source_event_id,
        source_file_path=source_file_path,
        source_url=source_url,
        raw_record_hash=_stable_hash(row),
        event_date=_parse_yyyymmdd(_value(row, "SQLDATE")),
        event_timestamp=_parse_event_timestamp(
            _value(row, "DATEADDED"),
            _value(row, "SQLDATE"),
        ),
        country_code=_empty_to_none(_value(row, "ActionGeo_CountryCode")),
        admin_region=_empty_to_none(_value(row, "ActionGeo_ADM1Code")),
        city=location_text,
        latitude=_to_float(_value(row, "ActionGeo_Lat")),
        longitude=_to_float(_value(row, "ActionGeo_Long")),
        geo_precision=_empty_to_none(_value(row, "ActionGeo_Type")),
        event_code=event_code,
        event_root_code=root_code,
        event_category=category,
        domain=Domain.SUPPLY_CHAIN if is_supply_chain_related else Domain.GENERAL,
        supply_chain_relevance_score=relevance_score,
        actor_1_name=actor_1_name,
        actor_1_country_code=_empty_to_none(_value(row, "Actor1CountryCode")),
        actor_1_type=_empty_to_none(_value(row, "Actor1Type1Code")),
        actor_2_name=actor_2_name,
        actor_2_country_code=_empty_to_none(_value(row, "Actor2CountryCode")),
        actor_2_type=_empty_to_none(_value(row, "Actor2Type1Code")),
        goldstein_score=_to_float(_value(row, "GoldsteinScale")),
        avg_tone=_to_float(_value(row, "AvgTone")),
        source_count=_to_int(_value(row, "NumSources")),
        mention_count=_to_int(_value(row, "NumMentions")),
        article_count=_to_int(_value(row, "NumArticles")),
        is_supply_chain_related=is_supply_chain_related,
        confidence_score=(
            SUPPLY_CHAIN_CONFIDENCE_SCORE
            if is_supply_chain_related
            else DEFAULT_CONFIDENCE_SCORE
        ),
        pipeline_run_id=pipeline_run_id,
        normalized_at=normalized_at,
        created_at=normalized_at,
        updated_at=normalized_at,
    )


def normalize_gdelt_events(
    rows: list[dict[str, str]],
    source_file_path: str | None = None,
    pipeline_run_id: UUID | None = None,
) -> list[NormalizedEvent]:
    """Normalize multiple parsed GDELT event rows."""
    return [normalize_gdelt_event(row, source_file_path, pipeline_run_id) for row in rows]


def _supply_chain_relevance_score(
    category: EventCategory,
    source_url: str | None,
    location_text: str | None,
    actor_names: tuple[str | None, str | None],
) -> float:
    score = 0.0
    if category in SUPPLY_CHAIN_CATEGORIES:
        score += SUPPLY_CHAIN_CATEGORY_SCORE
    if _contains_any_term(
        " ".join((source_url or "", location_text or "")),
        SUPPLY_CHAIN_LOCATION_TERMS,
    ):
        score += SUPPLY_CHAIN_KEYWORD_SCORE
    if _contains_any_term(
        " ".join(actor_name or "" for actor_name in actor_names),
        SUPPLY_CHAIN_ACTOR_TERMS,
    ):
        score += SUPPLY_CHAIN_KEYWORD_SCORE
    return min(score, 100.0)


def _stable_hash(row: dict[str, str]) -> str:
    serialized = "\t".join(f"{key}={row.get(key, '')}" for key in sorted(row))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _value(row: dict[str, str], field_name: str) -> str | None:
    return row.get(field_name) or row.get(_FIELD_ALIASES.get(field_name, ""))


def _contains_any_term(text: str, terms: tuple[str, ...]) -> bool:
    lowered_text = text.lower()
    return any(term in lowered_text for term in terms)


def _parse_yyyymmdd(value: str | None):
    if not value:
        return None
    return datetime.strptime(value, "%Y%m%d").date()


def _parse_yyyymmddhhmmss(value: str | None):
    if not value:
        return None
    date_format = "%Y%m%d" if len(value) == 8 else "%Y%m%d%H%M%S"
    return datetime.strptime(value, date_format).replace(tzinfo=timezone.utc)


def _parse_event_timestamp(date_added: str | None, sql_date: str | None):
    return _parse_yyyymmddhhmmss(date_added) or _parse_yyyymmddhhmmss(sql_date)


def _to_float(value: str | None) -> float | None:
    if value in (None, ""):
        return None
    return float(value)


def _to_int(value: str | None) -> int | None:
    if value in (None, ""):
        return None
    return int(value)


def _empty_to_none(value: str | None) -> str | None:
    return value or None
