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

