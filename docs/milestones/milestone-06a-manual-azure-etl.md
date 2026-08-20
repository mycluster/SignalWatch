# Milestone 06a - Manual Azure ETL Container Job

Date: 2026-08-20

## Goal

Validate the ETL worker as an Azure Container Apps Job using Azure storage, without requiring Postgres writes for this milestone.

The job must prove:

- container starts
- image pulls from ACR
- GDELT data can be downloaded/read
- bronze output can be written to ADLS
- normalized silver output can be written to ADLS
- job exits successfully

## Implementation

Added database-write gating:

- `ENABLE_DATABASE_WRITES=false` disables Postgres checkpoint/schema/upsert calls.
- With database writes disabled, `run-all` still downloads, parses, normalizes, writes bronze, writes silver, and exits based on ADLS success.

Added ADLS smoke-test command:

```powershell
python -m jobs.etl.main smoke-adls --storage azure
```

The smoke test writes unique tiny files using `CONTAINER_APP_JOB_EXECUTION_NAME`:

```text
bronze/_smoke_tests/job_execution=<execution-name>/bronze-test.txt
silver/_smoke_tests/job_execution=<execution-name>/silver-test.jsonl
```

Added idempotent-run behavior:

- already-processed windows now return `Status: skipped`
- skipped duplicate windows exit with code `0`
- `run-all --force` and `run-all --ignore-checkpoint` bypass checkpoint protection for manual testing only

## Azure Job Configuration

Container Apps Job:

```text
job-signalwatch-etl-dev
```

Resource group:

```text
rg-signalwatch-dev
```

Image:

```text
acrsignalwatchdev.azurecr.io/signalwatch-etl:dev
```

Important runtime settings:

```text
STORAGE_BACKEND=azure
ENABLE_DATABASE_WRITES=false
AZURE_STORAGE_ACCOUNT_NAME=stsignalwatchdev1
AZURE_STORAGE_CONTAINER_NAME=signalwatch
AZURE_STORAGE_ACCOUNT_URL=https://stsignalwatchdev1.dfs.core.windows.net
```

Job identity:

```text
SystemAssigned
```

Storage role assignments:

```text
Storage Blob Data Contributor
Storage Blob Data Owner
```

Resource sizing after validation:

```text
cpu: 1.0
memory: 2Gi
```

The original `0.5Gi` memory setting produced exit code `137` during the real ETL run.

## Validation Evidence

Evidence file:

```text
docs/evidence/milestone-06a-container-job-logs.txt
```

Successful smoke execution:

```text
job-signalwatch-etl-dev-zpqy7qi
Status: Succeeded
Exit code: 0
```

Successful real ADLS-only ETL execution:

```text
job-signalwatch-etl-dev-3hwa3gb
Status: Succeeded
Exit code: 0
Records read: 110686
Records normalized: 110686
Records written to Postgres: skipped
Records written to ADLS silver: 110686
```

Fresh real-run validation after smoke test:

```text
job-signalwatch-etl-dev-tf82rbf
Status: Succeeded
Exit code: 0
Pipeline: gdelt_run_all
Records read: 110686
Records normalized: 110686
Records written to Postgres: skipped
Records written to ADLS silver: 110686
```

Bronze output:

```text
abfss://signalwatch@stsignalwatchdev1.dfs.core.windows.net/bronze/gdelt/events/year=2026/month=08/day=19/hour=00/20260819.export.CSV.zip
```

Silver output:

```text
abfss://signalwatch@stsignalwatchdev1.dfs.core.windows.net/silver/normalized_events/year=2026/month=08/day=19/normalized-events-20260819.jsonl
```

## Result

Milestone 06a is complete. The Azure Container Apps Job can run the ETL container manually, authenticate to ADLS with managed identity, write bronze and silver outputs, skip Postgres writes, and exit successfully.
