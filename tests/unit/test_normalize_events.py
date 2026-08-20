"""Tests for GDELT event normalization."""

from uuid import UUID

from jobs.etl.transform.normalize_events import (
    GDELT_TO_NORMALIZED_FIELDS,
    normalize_gdelt_event,
)
from packages.signalwatch_common.enums import Domain, EventCategory


def test_normalize_gdelt_event_builds_normalized_model() -> None:
    event = normalize_gdelt_event(
        {
            "GLOBALEVENTID": "123",
            "SQLDATE": "20260820",
            "DATEADDED": "20260820123000",
            "EventCode": "141",
            "EventRootCode": "14",
            "Actor1Name": "PORT WORKERS",
            "Actor1CountryCode": "US",
            "Actor1Type1Code": "LAB",
            "Actor2Name": "PORT AUTHORITY",
            "Actor2CountryCode": "US",
            "Actor2Type1Code": "GOV",
            "GoldsteinScale": "-6.5",
            "AvgTone": "-2.1",
            "NumSources": "3",
            "NumMentions": "7",
            "NumArticles": "2",
            "ActionGeo_CountryCode": "US",
            "ActionGeo_ADM1Code": "USCA",
            "ActionGeo_FullName": "Los Angeles, California, United States",
            "ActionGeo_Lat": "34.0522",
            "ActionGeo_Long": "-118.2437",
            "ActionGeo_Type": "4",
            "SOURCEURL": "https://example.test/story",
        },
        source_file_path="data/raw/example.csv",
    )

    assert event.source_event_id == "123"
    assert event.event_category == EventCategory.PROTEST
    assert event.domain == Domain.SUPPLY_CHAIN
    assert event.is_supply_chain_related is True
    assert event.event_date.isoformat() == "2026-08-20"
    assert event.event_timestamp.isoformat() == "2026-08-20T12:30:00+00:00"
    assert event.latitude == 34.0522
    assert event.city == "Los Angeles, California, United States"


def test_gdelt_to_normalized_mapping_documents_requested_fields() -> None:
    assert GDELT_TO_NORMALIZED_FIELDS == {
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


def test_labor_action_marks_supply_chain_with_example_scores() -> None:
    event = normalize_gdelt_event(
        {
            "GLOBALEVENTID": "labor-1",
            "SQLDATE": "20260820",
            "EventCode": "143",
            "EventRootCode": "14",
        }
    )

    assert event.event_category == EventCategory.LABOR_ACTION
    assert event.domain == Domain.SUPPLY_CHAIN
    assert event.is_supply_chain_related is True
    assert event.supply_chain_relevance_score == 70.0
    assert event.confidence_score == 60.0


def test_supply_chain_keywords_in_source_url_or_location_mark_related() -> None:
    event = normalize_gdelt_event(
        {
            "GLOBALEVENTID": "port-1",
            "SQLDATE": "20260820",
            "EventCode": "010",
            "EventRootCode": "01",
            "ActionGeo_FullName": "Port of Houston, Texas, United States",
            "SOURCEURL": "https://example.test/fuel-logistics-delay",
        }
    )

    assert event.event_category == EventCategory.OTHER
    assert event.domain == Domain.SUPPLY_CHAIN
    assert event.supply_chain_relevance_score == 20.0
    assert event.confidence_score == 60.0


def test_supply_chain_actor_terms_mark_related() -> None:
    event = normalize_gdelt_event(
        {
            "GLOBALEVENTID": "actor-1",
            "SQLDATE": "20260820",
            "EventCode": "010",
            "EventRootCode": "01",
            "Actor1Name": "RAILWAY UNION",
            "Actor2Name": "TRUCK OPERATORS",
        }
    )

    assert event.domain == Domain.SUPPLY_CHAIN
    assert event.supply_chain_relevance_score == 20.0


def test_non_matching_event_stays_general() -> None:
    event = normalize_gdelt_event(
        {
            "GLOBALEVENTID": "general-1",
            "SQLDATE": "20260820",
            "EventCode": "010",
            "EventRootCode": "01",
            "Actor1Name": "CITY COUNCIL",
        }
    )

    assert event.domain == Domain.GENERAL
    assert event.is_supply_chain_related is False
    assert event.supply_chain_relevance_score == 0.0
    assert event.confidence_score == 30.0


def test_normalize_accepts_date_added_without_time_component() -> None:
    event = normalize_gdelt_event(
        {
            "GLOBALEVENTID": "daily-1",
            "SQLDATE": "20250818",
            "DATEADDED": "20260818",
            "EventCode": "010",
            "EventRootCode": "01",
        }
    )

    assert event.event_timestamp.isoformat() == "2026-08-18T00:00:00+00:00"


def test_normalize_populates_snowflake_lineage_fields() -> None:
    pipeline_run_id = UUID("00000000-0000-0000-0000-000000000123")

    event = normalize_gdelt_event(
        {
            "GLOBALEVENTID": "lineage-1",
            "SQLDATE": "20260820",
            "EventCode": "010",
            "EventRootCode": "01",
        },
        source_file_path="data/raw/gdelt/events/example.CSV.zip",
        pipeline_run_id=pipeline_run_id,
    )

    assert event.source_system == "GDELT"
    assert event.source_event_id == "lineage-1"
    assert event.source_file_path == "data/raw/gdelt/events/example.CSV.zip"
    assert event.raw_record_hash
    assert event.pipeline_run_id == pipeline_run_id
    assert event.event_timestamp.isoformat() == "2026-08-20T00:00:00+00:00"
    assert event.created_at.tzinfo is not None
    assert event.updated_at == event.created_at
