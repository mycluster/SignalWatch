"""Tests for GDELT event parsing."""

from zipfile import ZipFile

import pytest
from jobs.etl.transform.parse_gdelt_events import (
    GDELT_EVENT_FIELDS,
    parse_gdelt_events,
    parse_gdelt_events_file,
)


def test_parse_gdelt_events_maps_tab_delimited_row_to_fields() -> None:
    row = [""] * len(GDELT_EVENT_FIELDS)
    row[0] = "123"
    row[1] = "20260820"
    row[26] = "141"
    content = "\t".join(row)

    parsed = parse_gdelt_events(content)

    assert parsed == [
        {
            **dict.fromkeys(GDELT_EVENT_FIELDS, ""),
            "GLOBALEVENTID": "123",
            "SQLDATE": "20260820",
            "EventCode": "141",
        }
    ]


def test_parse_gdelt_events_file_reads_contained_csv_from_zip(tmp_path) -> None:
    row = [""] * len(GDELT_EVENT_FIELDS)
    row[0] = "123"
    row[1] = "20260820"
    row[26] = "141"
    raw_zip = tmp_path / "20260820000000.export.CSV.zip"

    with ZipFile(raw_zip, "w") as archive:
        archive.writestr("20260820000000.export.CSV", "\t".join(row))

    parsed = parse_gdelt_events_file(raw_zip)

    assert parsed[0]["GLOBALEVENTID"] == "123"
    assert parsed[0]["SQLDATE"] == "20260820"
    assert parsed[0]["EventCode"] == "141"


def test_parse_gdelt_events_file_requires_csv_inside_zip(tmp_path) -> None:
    raw_zip = tmp_path / "empty.export.CSV.zip"

    with ZipFile(raw_zip, "w") as archive:
        archive.writestr("README.txt", "not an event export")

    with pytest.raises(ValueError, match="No CSV file found"):
        parse_gdelt_events_file(raw_zip)
