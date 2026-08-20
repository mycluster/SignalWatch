"""Integration tests for normalized events API routes."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi.testclient import TestClient

from signalwatch.api.routes.events import get_event_service
from signalwatch.main import app

client = TestClient(app)


class FakeEventService:
    def __init__(self) -> None:
        self.list_kwargs = None

    def list_events(self, **kwargs):
        self.list_kwargs = kwargs
        return [
            {
                "id": UUID("00000000-0000-0000-0000-000000000001"),
                "source_event_id": "123456789",
                "event_timestamp": datetime(2026, 8, 20, tzinfo=timezone.utc),
                "country_code": "US",
                "event_category": "PROTEST",
                "domain": "SUPPLY_CHAIN",
                "is_supply_chain_related": True,
                "avg_tone": -3.4,
                "source_url": "https://example.com",
            }
        ]

    def get_event(self, event_id):
        if event_id != UUID("00000000-0000-0000-0000-000000000001"):
            return None
        return {
            "id": event_id,
            "source_system": "GDELT",
            "source_event_id": "123456789",
            "source_file_path": "data/raw/example.CSV.zip",
            "source_url": "https://example.com",
            "raw_record_hash": "abc123",
            "event_date": datetime(2026, 8, 20, tzinfo=timezone.utc).date(),
            "event_timestamp": datetime(2026, 8, 20, tzinfo=timezone.utc),
            "country_code": "US",
            "country_name": None,
            "admin_region": "USCA",
            "city": "Los Angeles, California, United States",
            "latitude": 34.0522,
            "longitude": -118.2437,
            "geo_precision": "4",
            "event_code": "141",
            "event_root_code": "14",
            "event_category": "PROTEST",
            "event_subcategory": None,
            "domain": "SUPPLY_CHAIN",
            "actor_1_name": "PORT WORKERS",
            "actor_1_country_code": "US",
            "actor_1_type": "LAB",
            "actor_2_name": "PORT AUTHORITY",
            "actor_2_country_code": "US",
            "actor_2_type": "GOV",
            "goldstein_score": -6.5,
            "avg_tone": -3.4,
            "source_count": 3,
            "mention_count": 7,
            "article_count": 2,
            "is_supply_chain_related": True,
            "supply_chain_relevance_score": 90.0,
            "confidence_score": 60.0,
            "pipeline_run_id": UUID("00000000-0000-0000-0000-000000000099"),
            "ingested_at": None,
            "normalized_at": datetime(2026, 8, 20, tzinfo=timezone.utc),
            "created_at": datetime(2026, 8, 20, tzinfo=timezone.utc),
            "updated_at": datetime(2026, 8, 20, tzinfo=timezone.utc),
        }


def test_get_events_returns_paginated_filtered_events() -> None:
    service = FakeEventService()
    app.dependency_overrides[get_event_service] = lambda: service

    response = client.get(
        "/events?country_code=US&event_category=PROTEST&domain=SUPPLY_CHAIN&limit=25"
    )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json() == {
        "count": 1,
        "limit": 25,
        "offset": 0,
        "events": [
            {
                "id": "00000000-0000-0000-0000-000000000001",
                "source_event_id": "123456789",
                "event_timestamp": "2026-08-20T00:00:00Z",
                "country_code": "US",
                "event_category": "PROTEST",
                "domain": "SUPPLY_CHAIN",
                "is_supply_chain_related": True,
                "avg_tone": -3.4,
                "source_url": "https://example.com",
            }
        ],
    }
    assert service.list_kwargs["country_code"] == "US"
    assert service.list_kwargs["event_category"] == "PROTEST"
    assert service.list_kwargs["limit"] == 25


def test_get_event_returns_full_detail() -> None:
    app.dependency_overrides[get_event_service] = lambda: FakeEventService()

    response = client.get("/events/00000000-0000-0000-0000-000000000001")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    body = response.json()
    assert body["source_event_id"] == "123456789"
    assert body["actor_1_name"] == "PORT WORKERS"
    assert body["pipeline_run_id"] == "00000000-0000-0000-0000-000000000099"


def test_get_event_returns_404_for_missing_event() -> None:
    app.dependency_overrides[get_event_service] = lambda: FakeEventService()

    response = client.get("/events/00000000-0000-0000-0000-000000000404")

    app.dependency_overrides.clear()
    assert response.status_code == 404
