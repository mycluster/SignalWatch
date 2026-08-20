##Milestone 1 -- Structure and health checks## 

Invoke-RestMethod -Uri 'http://127.0.0.1:8000/health' | ConvertTo-Json -Compress; Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/v1/health' | ConvertTo-Json -Compress


##Milestone 2 -- Ingesting from GDELT##
Command executed:
python -m jobs.etl.main ingest --window latest

Result: 
Pipeline: gdelt_events_ingestion
Window: 2026-08-18T00:00:00Z
Status: success
Records read: pending normalization
Raw path: data\raw\gdelt\events\year=2026\month=08\day=18\hour=00\20260818.export.CSV.zip




##Milestone 3 -- raw file -> Normalization##

Command Executed:
.\.venv\Scripts\python.exe -m jobs.etl.main normalize --raw-file "data/raw/gdelt/events/year=2026/month=08/day=18/hour=00/20260818.export.CSV.zip"

Result:
Pipeline: gdelt_events_ingestion
Raw file: data\raw\gdelt\events\year=2026\month=08\day=18\hour=00\20260818.export.CSV.zip
Status: success
Records read: 108538
Records written: 108538
Records failed: 0
Records normalized: 108538
Records after deduplication: 108538
Sample event id: 0bff25a4-0d4a-528c-9a22-2bdb43f123f6
Sample source event id: 1318712752

--Run twice for idemopotency check:

Result:
Pipeline: gdelt_events_ingestion
Raw file: data\raw\gdelt\events\year=2026\month=08\day=18\hour=00\20260818.export.CSV.zip
Status: success
Records read: 108538
Records written: 108538
Records failed: 0
Records normalized: 108538
Records after deduplication: 108538
Sample event id: 0bff25a4-0d4a-528c-9a22-2bdb43f123f6
Sample source event id: 1318712752

normalized_events count: 108538


General Examples
source_system | source_event_id | source_file_path | raw_record_hash | pipeline_run_id | event_timestamp | event_date | country_code | city | event_code | event_root_code | event_category | domain | is_supply_chain_related | supply_chain_relevance_score | avg_tone | source_url | created_at | updated_at
--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---
GDELT | 1318712752 | data\raw\gdelt\events\year=2026\month=08\day=18\hour=00\20260818.export.CSV.zip | 318dcdb4a43a0d678868559c28274889a3ade0af3ac2f4e2cdba060bc549df2b | c95ac93c-51b1-40bb-ac68-1e259cd89d78 | 2026-08-17 19:00:00-05:00 | 2025-08-18 | US | White Oak, Texas, United States | 010 | 01 | OTHER | GENERAL | False | 0.00 | -1.61 | https://www.wbrz.com/news/louisiana-ranks-last-in-the-country-for-nursing-home-care-quality | 2026-08-20 00:45:08.623522-05:00 | 2026-08-20 00:45:08.623522-05:00
GDELT | 1318712753 | data\raw\gdelt\events\year=2026\month=08\day=18\hour=00\20260818.export.CSV.zip | 721df86a7d0cb73288fa6035e0efca02acbf2a4128ccbfbb1e2f5e5ae7df2115 | c95ac93c-51b1-40bb-ac68-1e259cd89d78 | 2026-08-17 19:00:00-05:00 | 2025-08-18 | US | White Oak, Texas, United States | 010 | 01 | OTHER | GENERAL | False | 0.00 | -1.61 | https://www.wbrz.com/news/louisiana-ranks-last-in-the-country-for-nursing-home-care-quality | 2026-08-20 00:45:08.623522-05:00 | 2026-08-20 00:45:08.623522-05:00
Supply Chain Examples
source_system | source_event_id | source_file_path | raw_record_hash | pipeline_run_id | event_timestamp | event_date | country_code | city | event_code | event_root_code | event_category | domain | is_supply_chain_related | supply_chain_relevance_score | avg_tone | source_url | created_at | updated_at
--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---
GDELT | 1318715912 | data\raw\gdelt\events\year=2026\month=08\day=18\hour=00\20260818.export.CSV.zip | 37bb4217aab6e99f7e125a25734fdacde4dae4efe6f2ebc0d3fcf17f08867f31 | c95ac93c-51b1-40bb-ac68-1e259cd89d78 | 2026-08-17 19:00:00-05:00 | 2026-08-18 | US | Portland, Oregon, United States | 172 | 17 | TRANSPORT_DISRUPTION | SUPPLY_CHAIN | True | 100.00 | -3.41 | https://www.kotaradio.com/2026/08/17/portland-parent-banned-from-school-events-after-opposing-gender-identity-assignment | 2026-08-20 00:45:08.623522-05:00 | 2026-08-20 00:45:08.623522-05:00
GDELT | 1318743469 | data\raw\gdelt\events\year=2026\month=08\day=18\hour=00\20260818.export.CSV.zip | ef23916497d4a55031cfdd59f23453f5b957d4dcbab03c71bfc09d14db936baa | c95ac93c-51b1-40bb-ac68-1e259cd89d78 | 2026-08-17 19:00:00-05:00 | 2026-08-18 | US | Portland, Oregon, United States | 172 | 17 | TRANSPORT_DISRUPTION | SUPPLY_CHAIN | True | 100.00 | -0.32 | https://nypost.com/2026/08/18/us-news/portland-parent-banned-from-school-events-after-opposing-gender-identity-assignmen | 2026-08-20 00:45:08.623522-05:00 | 2026-08-20 00:45:08.623522-05:00




## MILESTONE 4  -- Event query and pipeline health APIs ##


GET /events- Pagination: limit, offset
- Filters: country_code, event_category, domain, is_supply_chain_related, since, until

GET /events/{event_id}- Full normalized event detail for drill-down/debugging

GET /pipeline/health- Latest pipeline status and record movement counts

GET /events?limit=2
{
  "count": 2,
  "limit": 2,
  "offset": 0,
  "events": [
    {
      "id": "0bff25a4-0d4a-528c-9a22-2bdb43f123f6",
      "source_event_id": "1318712752",
      "event_timestamp": "2026-08-17T19:00:00-05:00",
      "country_code": "US",
      "event_category": "OTHER",
      "domain": "GENERAL",
      "is_supply_chain_related": false,
      "avg_tone": -1.61,
      "source_url": "https://www.wbrz.com/news/louisiana-ranks-last-in-the-country-for-nursing-home-care-quality"
    }
  ]
}
GET /events?country_code=US&event_category=PROTEST&limit=2
{
  "count": 2,
  "limit": 2,
  "offset": 0,
  "events": [
    {
      "id": "035d0c58-bed1-5e0d-87df-708cd1ec54b8",
      "source_event_id": "1318713521",
      "event_timestamp": "2026-08-17T19:00:00-05:00",
      "country_code": "US",
      "event_category": "PROTEST",
      "domain": "GENERAL",
      "is_supply_chain_related": false,
      "avg_tone": -3.53,
      "source_url": "https://www.dailymail.com/news/article-16059617/So-White-House-hoaxer-duped-PM-Security-fears-Burnhams-messages-imposter-posed-Trumps-chief-staff.html"
    }
  ]
}
GET /events/{event_id}
{
  "id": "0bff25a4-0d4a-528c-9a22-2bdb43f123f6",
  "source_system": "GDELT",
  "source_event_id": "1318712752",
  "event_date": "2025-08-18",
  "event_timestamp": "2026-08-17T19:00:00-05:00",
  "country_code": "US",
  "admin_region": "USTX",
  "city": "White Oak, Texas, United States",
  "event_code": "010",
  "event_root_code": "01",
  "event_category": "OTHER",
  "domain": "GENERAL",
  "avg_tone": -1.61,
  "is_supply_chain_related": false,
  "supply_chain_relevance_score": 0.0,
  "pipeline_run_id": "c95ac93c-51b1-40bb-ac68-1e259cd89d78"
}
GET /pipeline/health
{
  "status": "healthy",
  "latest_pipeline": "gdelt_events_normalization",
  "latest_successful_run": "2026-08-20T00:45:21.786002-05:00",
  "records_read": 108538,
  "records_written": 108538,
  "records_failed": 0
}



Validation:

GET /events returns persisted normalized_events rows
GET /events supports pagination
GET /events supports country/category/domain/time filters
GET /events/{event_id} returns one event by UUID
unknown event_id returns 404
GET /pipeline/health returns latest pipeline status
API tests pass locally


## MILESTONE 5 -- End-to-end GDELT bronze, normalize, Postgres, silver ##

PS C:\Users\themi\OneDrive\Documents\signalWatch> .\.venv\Scripts\python.exe -m jobs.etl.main ingest --window latest --storage azure
Pipeline: gdelt_events_ingestion
Window: 2026-08-18T00:00:00Z
Status: success
Records read: 108538
Records written: 108538
Records failed: 0
Raw path: abfss://signalwatch@stsignalwatchdev1.dfs.core.windows.net/data/raw/gdelt/events/year=2026/month=08/day=18/hour=00/20260818.export.CSV.zip
Database verification output:
(UUID('e27792c8-ac50-4c28-83a0-35cfe31761cf'), 'success', datetime.datetime(2026, 8, 17, 19, 0, tzinfo=zoneinfo.ZoneInfo(key='America/Chicago')), datetime.datetime(2026, 8, 18, 19, 0, tzinfo=zoneinfo.ZoneInfo(key='America/Chicago')), 'abfss://signalwatch@stsignalwatchdev1.dfs.core.windows.net/data/raw/gdelt/events/year=2026/month=08/day=18/hour=00/20260818.export.CSV.zip', 108538, 108538, 0, 'http://data.gdeltproject.org/events/20260818.export.CSV.zip', datetime.datetime(2026, 8, 20, 1, 57, 22, 968228, tzinfo=zoneinfo.ZoneInfo(key='America/Chicago')))
Summary: GDELT file downloaded, raw file written to ADLS bronze path, and pipeline_runs.raw_output_path recorded successfully.




Command executed:
.\.venv\Scripts\python.exe -m jobs.etl.main run-all --window latest --storage azure

Result:
Pipeline: gdelt_run_all
Status: success
Storage backend: azure
Bronze path: abfss://signalwatch@stsignalwatchdev1.dfs.core.windows.net/bronze/gdelt/events/year=2026/month=08/day=19/hour=00/20260819.export.CSV.zip
Silver path: abfss://signalwatch@stsignalwatchdev1.dfs.core.windows.net/silver/normalized_events/year=2026/month=08/day=19/normalized-events-20260819.jsonl
Records read: 110686
Records normalized: 110686
Records written to Postgres: 110686
Records written to ADLS silver: 110686

Database verification output:
(UUID('382eedb1-2541-485c-9b9f-a14302f55ba3'), 'gdelt_run_all', 'success', 'azure', 'abfss://signalwatch@stsignalwatchdev1.dfs.core.windows.net/bronze/gdelt/events/year=2026/month=08/day=19/hour=00/20260819.export.CSV.zip', 'abfss://signalwatch@stsignalwatchdev1.dfs.core.windows.net/silver/normalized_events/year=2026/month=08/day=19/normalized-events-20260819.jsonl', 110686, 110686, 0, 'http://data.gdeltproject.org/events/20260819.export.CSV.zip', datetime.datetime(2026, 8, 20, 2, 7, 30, 548599, tzinfo=zoneinfo.ZoneInfo(key='America/Chicago')))

Summary: GDELT file downloaded, raw zip written to ADLS bronze, rows parsed and normalized, normalized rows persisted to Postgres, normalized JSONL written to ADLS silver, and pipeline_runs populated with raw_output_path, normalized_output_path, and storage_backend.


Pipeline: gdelt_run_all
Status: success
Storage backend: azure
Bronze path: abfss://signalwatch@stsignalwatchdev1.dfs.core.windows.net/bronze/gdelt/events/year=2026/month=08/day=19/hour=00/20260819.export.CSV.zip
Silver path: abfss://signalwatch@stsignalwatchdev1.dfs.core.windows.net/silver/normalized_events/year=2026/month=08/day=19/normalized-events-20260819.jsonl
Records read: 110686
Records normalized: 110686
Records written to Postgres: 110686
Records written to ADLS silver: 110686