"""Integration tests for pipeline health API routes."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi.testclient import TestClient

from signalwatch.api.routes.pipeline import get_pipeline_service
from signalwatch.main import app

client = TestClient(app)


class FakePipelineService:
    def get_health(self):
        return {
            "status": "healthy",
            "latest_pipeline": "gdelt_events_normalization",
            "latest_successful_run": datetime(2026, 8, 20, 0, 44, tzinfo=timezone.utc),
            "records_read": 2845,
            "records_written": 2810,
            "records_failed": 0,
        }


def test_pipeline_health_returns_latest_pipeline_status() -> None:
    app.dependency_overrides[get_pipeline_service] = lambda: FakePipelineService()

    response = client.get("/pipeline/health")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "latest_pipeline": "gdelt_events_normalization",
        "latest_successful_run": "2026-08-20T00:44:00Z",
        "records_read": 2845,
        "records_written": 2810,
        "records_failed": 0,
    }
