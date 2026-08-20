"""Parse GDELT Events export rows."""

from __future__ import annotations

import csv
import io
from collections.abc import Iterable
from pathlib import Path
from zipfile import ZipFile

# Field names are based on the GDELT 2.0 Event Codebook. GDELT event exports are
# published as .CSV.zip files, but the contained records are tab-delimited rows.
GDELT_EVENT_FIELDS = (
    "GLOBALEVENTID",
    "SQLDATE",
    "MonthYear",
    "Year",
    "FractionDate",
    "Actor1Code",
    "Actor1Name",
    "Actor1CountryCode",
    "Actor1KnownGroupCode",
    "Actor1EthnicCode",
    "Actor1Religion1Code",
    "Actor1Religion2Code",
    "Actor1Type1Code",
    "Actor1Type2Code",
    "Actor1Type3Code",
    "Actor2Code",
    "Actor2Name",
    "Actor2CountryCode",
    "Actor2KnownGroupCode",
    "Actor2EthnicCode",
    "Actor2Religion1Code",
    "Actor2Religion2Code",
    "Actor2Type1Code",
    "Actor2Type2Code",
    "Actor2Type3Code",
    "IsRootEvent",
    "EventCode",
    "EventBaseCode",
    "EventRootCode",
    "QuadClass",
    "GoldsteinScale",
    "NumMentions",
    "NumSources",
    "NumArticles",
    "AvgTone",
    "Actor1Geo_Type",
    "Actor1Geo_FullName",
    "Actor1Geo_CountryCode",
    "Actor1Geo_ADM1Code",
    "Actor1Geo_Lat",
    "Actor1Geo_Long",
    "Actor1Geo_FeatureID",
    "Actor2Geo_Type",
    "Actor2Geo_FullName",
    "Actor2Geo_CountryCode",
    "Actor2Geo_ADM1Code",
    "Actor2Geo_Lat",
    "Actor2Geo_Long",
    "Actor2Geo_FeatureID",
    "ActionGeo_Type",
    "ActionGeo_FullName",
    "ActionGeo_CountryCode",
    "ActionGeo_ADM1Code",
    "ActionGeo_Lat",
    "ActionGeo_Long",
    "ActionGeo_FeatureID",
    "DATEADDED",
    "SOURCEURL",
)


def parse_gdelt_events(content: str | bytes) -> list[dict[str, str]]:
    """Parse tab-delimited GDELT Events export content into dictionaries."""
    text = content.decode("utf-8") if isinstance(content, bytes) else content
    rows = csv.reader(io.StringIO(text), delimiter="\t")
    return [dict(zip(GDELT_EVENT_FIELDS, _pad_row(row))) for row in rows if row]


def parse_gdelt_events_file(raw_file: str | Path) -> list[dict[str, str]]:
    """Open a raw GDELT Events CSV or CSV zip and return raw event dictionaries."""
    raw_path = Path(raw_file)
    return parse_gdelt_events(_read_raw_events_file(raw_path))


def iter_gdelt_events(lines: Iterable[str]) -> Iterable[dict[str, str]]:
    """Yield parsed GDELT rows from an iterable of tab-delimited lines."""
    rows = csv.reader(lines, delimiter="\t")
    for row in rows:
        if row:
            yield dict(zip(GDELT_EVENT_FIELDS, _pad_row(row)))


def _read_raw_events_file(raw_path: Path) -> bytes:
    if raw_path.suffix.lower() != ".zip":
        return raw_path.read_bytes()

    with ZipFile(raw_path) as archive:
        csv_names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
        if not csv_names:
            raise ValueError(f"No CSV file found inside {raw_path}")
        with archive.open(csv_names[0]) as csv_file:
            return csv_file.read()


def _pad_row(row: list[str]) -> list[str]:
    if len(row) >= len(GDELT_EVENT_FIELDS):
        return row[: len(GDELT_EVENT_FIELDS)]
    return [*row, *([""] * (len(GDELT_EVENT_FIELDS) - len(row)))]
