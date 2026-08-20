"""Tests for normalized-event persistence."""

from uuid import UUID

from jobs.etl.transform.normalize_events import normalize_gdelt_event
from jobs.etl.transform.normalized_event_writer import NormalizedEventWriter


class FakeCursor:
    rowcount = 0

    def __init__(self) -> None:
        self.statements = []
        self.executemany_calls = []

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return None

    def execute(self, statement, parameters=None) -> None:
        self.statements.append((statement, parameters))

    def executemany(self, statement, parameters) -> None:
        self.executemany_calls.append((statement, parameters))
        self.rowcount = len(parameters)


class FakeConnection:
    def __init__(self, cursor) -> None:
        self.fake_cursor = cursor

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return None

    def cursor(self):
        return self.fake_cursor


def test_upsert_events_writes_normalized_events_with_conflict_handling() -> None:
    cursor = FakeCursor()
    writer = NormalizedEventWriter(
        connection_factory=lambda _: FakeConnection(cursor),
    )
    event = normalize_gdelt_event(
        {
            "GLOBALEVENTID": "123",
            "SQLDATE": "20260820",
            "EventCode": "143",
            "EventRootCode": "14",
        },
        pipeline_run_id=UUID("00000000-0000-0000-0000-000000000123"),
    )

    written = writer.upsert_events([event])

    statement, parameters = cursor.executemany_calls[0]
    assert written == 1
    assert "INSERT INTO normalized_events" in statement
    assert "ON CONFLICT (source_system, source_event_id)" in statement
    assert parameters[0][2] == "123"
    assert parameters[0][17] == "LABOR_ACTION"
    assert parameters[0][19] == "SUPPLY_CHAIN"
    assert parameters[0][34] == UUID("00000000-0000-0000-0000-000000000123")
    assert parameters[0][36] == event.created_at
    assert parameters[0][37] == event.updated_at
