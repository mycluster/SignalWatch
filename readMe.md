# SignalWatch

## GDELT-Powered Global Event Monitoring Platform

SignalWatch is a production-style data engineering and platform project that ingests GDELT global event data, normalizes raw event records, stores queryable data locally and in cloud storage, and prepares curated outputs for downstream analytics in Snowflake.

The project is designed to demonstrate backend engineering, data pipeline development, cloud/platform operations, CI/CD, data quality, observability, and warehouse integration.

---

## Project Purpose

SignalWatch converts noisy public event data into a structured event intelligence platform.

The initial focus is supply-chain risk monitoring. The system ingests GDELT event files, normalizes them into a stable internal schema, persists records to Postgres for API access, and will later publish curated datasets to Azure Data Lake Storage Gen2 and Snowflake.

The goal is not simply to download a public dataset or build a dashboard. The goal is to build an operated data platform with clear ingestion, persistence, lineage, cloud storage, automation, observability, and analytical serving layers.

---

## Current Project Status

The project has completed the local foundation and raw ingestion milestones.

Completed:

* Local project skeleton
* Docker Compose runtime foundation
* FastAPI health endpoint
* Postgres local dependency
* GitHub Actions CI validation
* GDELT raw file download workflow
* Local raw file validation
* In-memory normalization workflow
* Persistence of normalized GDELT events to Postgres

Current focus:

* Expose persisted normalized events through FastAPI endpoints
* Prepare Azure Data Lake Storage Gen2 as the cloud dataset destination
* Add Snowflake as an optional downstream analytical warehouse layer

---

## High-Level Architecture

```text
GDELT Event Files
        ↓
ETL Worker
        ↓
Raw Local Storage / Azure Data Lake Bronze
        ↓
Normalization Pipeline
        ↓
Postgres Serving Tables
        ↓
FastAPI Event Query API
        ↓
Azure Data Lake Silver/Gold Outputs
        ↓
Snowflake Analytics Layer
```

---

## Target Cloud Architecture

```text
GitHub Repository
        ↓
GitHub Actions CI/CD
        ↓
Azure Container Registry
        ↓
Azure Container Apps
        ├── FastAPI service
        └── Scheduled ETL job
                ↓
Azure Data Lake Storage Gen2
        ├── bronze/raw
        ├── silver/normalized
        └── gold/curated
                ↓
Snowflake
        ├── external stage
        ├── COPY INTO batch loads
        └── optional Snowpipe auto-ingest
```

---

## Storage Strategy

SignalWatch uses separate storage layers for different responsibilities.

### Postgres

Postgres is used for local and API-serving workloads.

Responsibilities:

* Store `pipeline_runs`
* Store `normalized_events`
* Support FastAPI queries
* Support pagination and filters
* Support local development and validation

### Azure Data Lake Storage Gen2

Azure Data Lake Storage Gen2 is the cloud system of record for dataset files.

Responsibilities:

* Store raw GDELT files
* Store normalized event outputs
* Store curated risk and analytics outputs
* Support replayability and lineage
* Provide a durable cloud data lake destination

Planned layout:

```text
signalwatch/
  bronze/
    gdelt/
      events/
        year=YYYY/
          month=MM/
            day=DD/
              hour=HH/
                <gdelt-file>.CSV.zip

  silver/
    normalized_events/
      year=YYYY/
        month=MM/
          day=DD/
            normalized-events.parquet

  gold/
    analytics/
      risk_scores/
      event_trends/
      supply_chain_hotspots/

  checkpoints/
    gdelt/
      event_ingestion_checkpoint.json

  quality/
    data_quality_results/
```

### Snowflake

Snowflake is an optional downstream analytics layer.

Responsibilities:

* Load curated Azure Data Lake outputs
* Support analytical SQL queries
* Validate warehouse ingestion patterns
* Demonstrate Snowflake external stage usage
* Demonstrate batch load and optional Snowpipe design

Snowflake should not replace Azure Data Lake Storage or Postgres.

Recommended role:

```text
Azure Data Lake Gen2 = durable cloud dataset destination
Postgres = API serving and operational metadata
Snowflake = analytics warehouse and reporting layer
```

---

## Current Local Flow

The current local flow is:

```text
Download GDELT file
        ↓
Save raw file locally
        ↓
Parse raw .CSV.zip file
        ↓
Normalize event records
        ↓
Persist normalized events to Postgres
        ↓
Track pipeline run metadata
```

This proves that SignalWatch can move from raw public data to queryable internal records.

---

## Repository Structure

```text
signalWatch/
  README.md
  docker-compose.yml
  pyproject.toml
  .env.example

  .github/
    workflows/
      ci.yml
      build-api.yml
      build-etl.yml
      deploy-azure.yml

  apps/
    api/
      Dockerfile
      main.py
      routes/
        events.py
        pipeline.py
      schemas/
        events.py
        pipeline.py
      services/
        event_service.py
        pipeline_service.py

  jobs/
    etl/
      Dockerfile
      main.py
      ingest/
        gdelt_client.py
        raw_writer.py
        checkpoint_service.py
      transform/
        parse_gdelt_events.py
        normalize_events.py
        event_category_mapper.py
        deduplicate.py
      load/
        normalized_event_repository.py
        adls_writer.py
        snowflake_loader.py
      quality/
        checks.py
        result_writer.py
      scoring/
        risk_score.py
        baselines.py
        alerts.py

  packages/
    signalwatch_common/
      config.py
      logging.py
      enums.py
      azure_clients.py
      models/
        normalized_event.py
        pipeline_run.py
        quality_result.py

  db/
    schema/
      pipeline_runs.sql
      normalized_events.sql
      data_quality_results.sql
      alerts.sql
      watchlists.sql
    migrations/
    seeds/

  infra/
    terraform/
      modules/
        resource_group/
        storage_account/
        container_registry/
        container_apps/
        container_apps_job/
        postgres/
        key_vault/
        log_analytics/
      environments/
        dev/
        prod/

  snowflake/
    sql/
      001_create_database.sql
      002_create_storage_integration.sql
      003_create_file_format.sql
      004_create_external_stage.sql
      005_create_tables.sql
      006_copy_into_normalized_events.sql
      007_create_views.sql
    worksheets/
      validation_queries.sql
      supply_chain_analysis.sql
    docs/
      snowflake-setup.md
      snowflake-load-runbook.md

  observability/
    grafana/
      dashboards/
    prometheus/
    log_queries/

  docs/
    architecture.md
    azure-deployment.md
    data-model.md
    etl-flow.md
    operations-runbook.md
    evaluation.md
    limitations.md
    milestones/

  tests/
    unit/
    integration/
    contract/
```

---

## Milestone Roadmap

## Milestone 1: Local Runtime Foundation

### Objective

Create a clean local development foundation that supports the API, database, tests, and CI validation.

### Completed Scope

* Created project skeleton
* Added Docker Compose
* Added local Postgres
* Added FastAPI health endpoint
* Added test framework
* Added linting and formatting
* Added GitHub Actions CI validation
* Added basic Docker build validation

### Status

Complete.

---

## Milestone 2: GDELT Raw Ingestion Workflow

### Objective

Download a GDELT event file and store it locally as a raw source artifact.

### Completed Scope

* Added GDELT ingestion client
* Added local raw file writer
* Added ETL CLI entrypoint
* Downloaded a raw GDELT file locally
* Validated that the file lands on the local machine
* Added pipeline run tracking for ingestion attempts

### Status

Complete.

---

## Milestone 3: Normalize and Persist GDELT Events

### Objective

Parse a downloaded GDELT `.CSV.zip` file, normalize the rows into the internal event schema, and persist normalized records to Postgres.

### Completed Scope

* Parsed raw GDELT event files
* Normalized rows into internal event objects
* Applied initial event field mapping
* Added event category mapping
* Added basic supply-chain relevance logic
* Added `normalized_events` persistence
* Inserted normalized rows into Postgres
* Preserved source lineage fields
* Updated pipeline run metadata

### Status

Complete.

### Completion Evidence

Recommended evidence location:

```text
docs/milestones/milestone-03-normalization.md
docs/evidence/milestone-03-normalization-console.txt
```

Recommended validation evidence:

```text
- Raw file exists locally
- Normalize command runs successfully
- Records are persisted to normalized_events
- pipeline_runs records read/write/failure counts
- Duplicate-safe rerun behavior is validated
- Tests pass locally and in GitHub Actions
```

---

## Milestone 4: Event Query API

### Objective

Expose persisted normalized events through FastAPI.

### Scope

* Add `GET /events`
* Add `GET /events/{event_id}`
* Add `GET /pipeline/health`
* Support pagination
* Support filters by country, event category, domain, supply-chain relevance, and time window
* Add API response schemas
* Add event service layer
* Add pipeline health service
* Add API integration tests

### Deliverables

* Queryable event API
* Event detail endpoint
* Pipeline health endpoint
* API test coverage
* README usage examples

### Success Criteria

```text
- GET /events returns persisted normalized_events rows
- GET /events supports pagination
- GET /events supports basic filters
- GET /events/{event_id} returns one event by UUID
- Unknown event IDs return 404
- GET /pipeline/health returns latest pipeline status
- Tests pass locally
- GitHub Actions passes
```

---

## Milestone 5: Azure Data Lake Storage Integration

### Objective

Move dataset storage from local-only files to Azure Data Lake Storage Gen2.

### Scope

* Provision Azure Storage Account with hierarchical namespace enabled
* Create ADLS container and folder structure
* Add Azure Data Lake writer
* Write raw GDELT files to bronze storage
* Write normalized event outputs to silver storage
* Add cloud-compatible checkpoint location
* Preserve local writer as a development option
* Add configuration switch for local versus Azure storage

### Deliverables

* ADLS-backed raw storage
* ADLS-backed normalized output
* Azure storage client integration
* Documented data lake layout
* Azure deployment notes

### Success Criteria

```text
- ETL can write raw files to ADLS bronze
- ETL can write normalized outputs to ADLS silver
- Local mode still works
- Storage destination is configurable
- Credentials are not hardcoded
```

---

## Milestone 6: Azure ETL Runtime

### Objective

Run the ETL workflow as a scheduled Azure workload.

### Scope

* Containerize the ETL worker
* Push ETL image to Azure Container Registry
* Deploy ETL as an Azure Container Apps Job
* Configure recurring schedule
* Configure managed identity or secure credential access
* Connect ETL job to ADLS
* Connect ETL job to Postgres
* Add logs for each cloud run

### Deliverables

* ETL Docker image
* Azure Container Registry repository
* Scheduled Azure Container Apps Job
* Cloud ETL run logs
* Cloud ETL run documentation

### Success Criteria

```text
- ETL runs from Azure
- ETL writes to ADLS
- ETL updates pipeline metadata
- ETL can be run manually
- ETL can run on a schedule
```

---

## Milestone 7: GitHub Actions to Azure CI/CD

### Objective

Deploy application and ETL changes to Azure using GitHub Actions.

### Scope

* Add GitHub Actions workflow for Azure login
* Use OpenID Connect authentication
* Build API Docker image
* Build ETL Docker image
* Push images to Azure Container Registry
* Deploy or update Azure Container App
* Deploy or update Azure Container Apps Job
* Add environment-specific workflow configuration

### Deliverables

* GitHub Actions Azure deployment workflow
* ACR image publishing
* API deployment workflow
* ETL job deployment workflow
* Documented CI/CD process

### Success Criteria

```text
- Pull requests run lint and tests
- Merges to main build container images
- Images are pushed to Azure Container Registry
- Azure workloads are updated from GitHub Actions
- No long-lived Azure credentials are stored in the repository
```

---

## Milestone 8: Snowflake Batch Load Integration

### Objective

Load curated SignalWatch outputs from Azure Data Lake Storage into Snowflake for analytical querying.

### Scope

* Create Snowflake database and schema
* Create Snowflake warehouse
* Create Azure storage integration
* Create external stage over ADLS gold or silver path
* Create file format
* Create Snowflake tables
* Add batch `COPY INTO` load scripts
* Add validation queries
* Document Snowflake setup

### Deliverables

* Snowflake setup SQL
* External stage definition
* `COPY INTO` load script
* Snowflake `NORMALIZED_EVENTS` table
* Validation worksheet
* Snowflake load runbook

### Success Criteria

```text
- Snowflake can access the configured Azure storage path
- Curated files can be loaded into Snowflake
- Loaded row counts can be reconciled against ADLS/Postgres
- Validation queries return expected results
- Setup is documented
```

---

## Milestone 9: Snowflake Analytics Views

### Objective

Create Snowflake analytical views that demonstrate warehouse-level querying.

### Scope

* Create supply-chain event trend view
* Create country/category aggregation view
* Create high-risk event view
* Create source coverage view
* Create pipeline load audit view
* Add example analytical SQL queries

### Deliverables

* Snowflake views
* Analytical worksheets
* Example query results
* Documentation showing how Snowflake adds value beyond the API

### Success Criteria

```text
- Snowflake can answer aggregate analytical questions
- Views are documented
- Example queries support portfolio/demo storytelling
```

---

## Milestone 10: Optional Snowpipe Auto-Ingest

### Objective

Automate continuous loading from Azure storage into Snowflake.

### Scope

* Configure Azure Event Grid integration
* Create Snowflake notification integration
* Create Snowpipe pipe
* Enable auto-ingest
* Add load monitoring queries
* Add error handling documentation

### Deliverables

* Snowpipe setup SQL
* Event Grid integration notes
* Auto-ingest pipe
* Snowpipe monitoring queries
* Snowpipe troubleshooting notes

### Success Criteria

```text
- New eligible files in Azure trigger Snowflake ingestion
- Snowpipe load history shows successful file loads
- Failed loads can be diagnosed
- Auto-ingest behavior is documented
```

---

## Milestone 11: Risk Scoring and Data Quality

### Objective

Add analytical intelligence and trust signals to the platform.

### Scope

* Create rolling event baselines
* Detect event volume spikes
* Implement simple risk scoring
* Store risk score history
* Add data quality checks
* Track freshness
* Track duplicate rates
* Track null location rates
* Track unmapped category rates
* Expose quality results through API

### Deliverables

* Risk scoring job
* Risk score table
* Data quality results table
* Data quality API response
* Freshness checks
* Duplicate-rate checks
* Tests for scoring and validation rules

### Success Criteria

```text
- System can detect abnormal event activity
- Risk scores include explanation fields
- Data quality checks are stored
- Data freshness is visible
- Quality checks can fail without silently corrupting the pipeline
```

---

## Milestone 12: Observability and Dashboard

### Objective

Make the platform easy to monitor and demo.

### Scope

* Add structured logging
* Add service metrics
* Add API latency metrics
* Add ingestion metrics
* Add pipeline failure metrics
* Add Grafana dashboard
* Add dashboard UI for event trends and alerts
* Add operational runbook

### Deliverables

* Observability dashboard
* User-facing dashboard
* Pipeline health panel
* Event trend visualization
* Alert/risk summary view
* Runbook documentation

### Success Criteria

```text
- System health can be assessed without manually reading raw logs
- Event trends are visible in a dashboard
- Pipeline freshness is visible
- Demo flow is clear and repeatable
```

---

## Snowflake Integration Design

Snowflake is intentionally downstream from Azure Data Lake Storage.

Recommended data flow:

```text
ETL writes curated files to ADLS
        ↓
Snowflake external stage points to ADLS path
        ↓
COPY INTO loads files into Snowflake tables
        ↓
Snowflake views expose analytical summaries
        ↓
Optional Snowpipe automates continuous loading later
```

Initial Snowflake objects:

```text
Database:
  SIGNALWATCH

Schemas:
  RAW
  CURATED
  ANALYTICS
  AUDIT

Tables:
  CURATED.NORMALIZED_EVENTS
  AUDIT.LOAD_HISTORY
  AUDIT.PIPELINE_RUNS

Views:
  ANALYTICS.SUPPLY_CHAIN_EVENT_TRENDS
  ANALYTICS.EVENTS_BY_COUNTRY
  ANALYTICS.HIGH_RISK_EVENTS
  ANALYTICS.SOURCE_COVERAGE
```

Snowflake should answer questions like:

```text
- Which countries have the highest supply-chain-related event volume?
- Which event categories are increasing over time?
- How many events were loaded by batch?
- Are Snowflake row counts reconciled with Azure and Postgres?
- Which sources or regions show abnormal coverage patterns?
```

---

## CI/CD Strategy

GitHub Actions is responsible for validation and deployment.

Pull request workflow:

```text
- install dependencies
- run lint checks
- run formatting check
- run unit tests
- run integration tests where available
- validate Docker builds
```

Main branch workflow:

```text
- build API image
- build ETL image
- push images to Azure Container Registry
- deploy FastAPI app to Azure Container Apps
- deploy scheduled ETL job to Azure Container Apps Jobs
```

Snowflake deployment workflow, later:

```text
- validate SQL scripts
- apply Snowflake setup scripts manually at first
- automate Snowflake object deployment only after the SQL stabilizes
```

Recommended rule:

```text
Automate Azure deployment first.
Keep Snowflake setup script-based until the warehouse model stabilizes.
```

---

## Local Development Commands

Start local dependencies:

```bash
docker compose up -d
```

Run API:

```bash
uvicorn apps.api.main:app --reload
```

Run tests:

```bash
pytest
```

Run raw ingestion:

```bash
python -m jobs.etl.main ingest --window latest
```

Run normalization:

```bash
python -m jobs.etl.main normalize --raw-file <path-to-gdelt-csv-zip>
```

Run full local ETL, once available:

```bash
python -m jobs.etl.main run-all --window latest
```

---

## API Roadmap

Initial API endpoints:

```http
GET /health
GET /events
GET /events/{event_id}
GET /pipeline/health
```

Future API endpoints:

```http
GET /risk/hotspots
GET /risk/timeseries
GET /quality/status
GET /alerts
POST /watchlists
GET /watchlists
GET /watchlists/{watchlist_id}
```

---

## Data Model Direction

Current core tables:

```text
pipeline_runs
normalized_events
```

Near-term tables:

```text
data_quality_results
risk_scores
alerts
watchlists
```

Snowflake tables:

```text
CURATED.NORMALIZED_EVENTS
AUDIT.PIPELINE_RUNS
AUDIT.LOAD_HISTORY
ANALYTICS views
```

Important design principle:

```text
Postgres supports the application.
Azure Data Lake stores the dataset.
Snowflake supports analytical querying.
```

---

## Known Limitations

SignalWatch should not treat GDELT as perfect ground truth.

Important limitations:

* GDELT reflects media/event signals, not verified incident counts
* News coverage varies by geography, language, and source availability
* Event classification may be imperfect
* Duplicate or near-duplicate events may appear
* Some records may lack precise location data
* Tone does not always equal operational severity
* High media coverage does not always mean high operational risk
* Low media coverage does not always mean low operational risk

The platform should expose data quality, freshness, lineage, and confidence signals rather than pretending the dataset is perfect.

---

## Portfolio Positioning

SignalWatch demonstrates the ability to build a cloud-ready data platform around messy, frequently updated public data.

Strong project description:

> Built a GDELT-powered event intelligence platform that ingests raw global event files, normalizes records into a stable internal schema, persists queryable events to Postgres, prepares curated outputs for Azure Data Lake Storage Gen2, and integrates Snowflake as a downstream analytics warehouse.

Resume-ready bullets:

* Built a Python/FastAPI data platform that ingests GDELT global event files, normalizes raw event records, and persists queryable results to Postgres.
* Designed a cloud-ready ETL architecture targeting Azure Data Lake Storage Gen2 with bronze, silver, and gold dataset layers.
* Added pipeline metadata tracking, source lineage, and duplicate-safe persistence for normalized event records.
* Planned Snowflake integration using Azure external stages, batch `COPY INTO` loads, audit tables, and analytical views.
* Designed CI/CD workflow using GitHub Actions, container builds, Azure deployment targets, and secure cloud authentication patterns.
