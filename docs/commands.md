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
source_event_id | event_date | event_category | domain | is_supply_chain_related | supply_chain_relevance_score | country_code | city
--- | --- | --- | --- | --- | --- | --- | ---
1318712752 | 2025-08-18 | OTHER | GENERAL | False | 0.00 | US | White Oak, Texas, United States
1318712753 | 2025-08-18 | OTHER | GENERAL | False | 0.00 | US | White Oak, Texas, United States
1318712754 | 2025-08-18 | GOVERNMENT_ACTION | GENERAL | False | 0.00 | US | New York, United States
1318712755 | 2025-08-18 | GOVERNMENT_ACTION | GENERAL | False | 0.00 | US | New York, United States
1318712756 | 2025-08-18 | GOVERNMENT_ACTION | GENERAL | False | 0.00 | IN | India


--Rows where supply chain score is not 0
source_event_id | event_date | event_category | domain | is_supply_chain_related | supply_chain_relevance_score | country_code | city | source_url
--- | --- | --- | --- | --- | --- | --- | --- | ---
1318715912 | 2026-08-18 | TRANSPORT_DISRUPTION | SUPPLY_CHAIN | True | 100.00 | US | Portland, Oregon, United States | https://www.kotaradio.com/2026/08/17/portland-parent-banned-from-school-events-after-opposing-gender
1318743469 | 2026-08-18 | TRANSPORT_DISRUPTION | SUPPLY_CHAIN | True | 100.00 | US | Portland, Oregon, United States | https://nypost.com/2026/08/18/us-news/portland-parent-banned-from-school-events-after-opposing-gende
1318782833 | 2026-08-18 | TRANSPORT_DISRUPTION | SUPPLY_CHAIN | True | 100.00 | US | Portland, Oregon, United States | https://timesofindia.indiatimes.com/world/us/us-mother-sues-portland-public-school-after-being-barre
1318812987 | 2026-08-18 | TRANSPORT_DISRUPTION | SUPPLY_CHAIN | True | 100.00 | US | Portland Community College, Oregon, United States | https://dailycoffeenews.com/2026/08/18/clarks-coffee-brings-fresh-energy-to-former-stumptown-space-i
1318713952 | 2026-08-18 | TRANSPORT_DISRUPTION | SUPPLY_CHAIN | True | 90.00 | UP | Ukraine | https://www.wsws.org/en/articles/2026/08/17/smoq-a17.html
1318717231 | 2026-08-18 | TRANSPORT_DISRUPTION | SUPPLY_CHAIN | True | 90.00 |  |  | https://www.niagarafallsreview.ca/news/niagara-region/5-people-injured-in-port-colborne-collision/ar
1318717803 | 2026-08-18 | TRANSPORT_DISRUPTION | SUPPLY_CHAIN | True | 90.00 | IR | Tehran, Tehran, Iran | http://www.middleeaststar.com/news/279247275/60-day-deadline-expires-for-us-iran-talks-under-framewo
1318725341 | 2026-08-18 | TRANSPORT_DISRUPTION | SUPPLY_CHAIN | True | 90.00 | US | Big Bend National Park, Texas, United States | https://www.newsweek.com/trump-big-bend-border-construction-paused-rodney-scott-review-12333849