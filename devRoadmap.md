# SignalWatch Development Roadmap

SignalWatch is organized around engineering milestones rather than fixed delivery dates. The roadmap originally placed cloud deployment near the end of the project. During implementation, cloud storage, runtime deployment, and CI/CD were moved earlier so later analytical and alerting features can be built on a repeatable Azure foundation.

The product direction has not changed. Watchlists, alerts, risk scoring, data quality, observability, and the dashboard remain planned; their milestone numbers changed to accommodate the cloud-first build order.

## Status Legend

- **Complete** — implemented and verified
- **In progress** — current milestone
- **Planned** — not yet started
- **Optional** — valuable extension that is not required for the core portfolio project

---

## Milestone 1: Local Runtime Foundation — Complete

### Objective

Create a maintainable local development foundation for the API, database, tests, containers, and CI validation.

### Delivered

- Python project structure
- Docker Compose runtime
- Local PostgreSQL dependency
- FastAPI health endpoint
- Test framework
- Linting and formatting
- GitHub Actions CI validation
- Docker build validation

### Success Criteria

The repository can be cloned, started locally, and validated through passing health, lint, test, and container-build checks.

---

## Milestone 2: GDELT Raw Ingestion Workflow — Complete

### Objective

Download a defined GDELT event window and persist the raw source artifact with operational metadata.

### Delivered

- GDELT ingestion client
- Local raw file writer
- ETL CLI entry point
- Raw download validation
- `pipeline_runs` tracking
- Failure handling, retry behavior, and structured logs
- Tests for the ingestion workflow

### Success Criteria

One command downloads a GDELT event window, stores the raw file, and records the pipeline attempt without manual state changes.

---

## Milestone 3: Normalize and Persist GDELT Events — Complete

### Objective

Transform raw GDELT records into stable internal event records and persist them for application queries.

### Delivered

- Raw `.CSV.zip` parsing
- Normalized event model
- Timestamp, location, actor, source, and event-code mapping
- Initial supply-chain relevance classification
- Deduplication and duplicate-safe reruns
- PostgreSQL persistence
- Raw-source lineage fields
- Pipeline read, write, and failure counts
- Transformation tests

### Success Criteria

Raw files are converted into queryable normalized records while preserving lineage and safe replay behavior.

---

## Milestone 4: Event Query API — Complete

### Objective

Expose persisted normalized events and pipeline state through FastAPI.

### Delivered

- `GET /events`
- `GET /events/{event_id}`
- Pagination and event filters
- Typed response schemas
- Event service layer
- Pipeline health endpoint
- API tests and OpenAPI documentation

### Success Criteria

Users can query normalized events by geography, category, domain, supply-chain relevance, and time window, and can inspect the latest pipeline status.

---

## Milestone 5: Azure Data Lake Storage Integration — Complete

### Objective

Move dataset artifacts from local-only storage to Azure Data Lake Storage Gen2 while retaining local development support.

### Delivered

- ADLS Gen2 storage account and container
- Bronze path for raw GDELT `.CSV.zip` files
- Silver path for normalized Parquet output
- Azure storage writer
- Configurable local or Azure storage backend
- Cloud-compatible pathing and source lineage
- Credential configuration without hardcoding secrets

### Success Criteria

The ETL pipeline writes raw data to bronze and normalized Parquet data to silver, while local storage mode continues to work.

---

## Milestone 6: Azure ETL Runtime — Complete

### Objective

Run the ETL workflow as an Azure Container Apps Job connected to ADLS and operational logging.

### Delivered

- ETL Docker image
- Azure Container Registry repository
- Azure Container Apps Job
- Runtime environment configuration
- ADLS connectivity
- Cloud execution logs
- Manual job execution
- Verified successful cloud run

### Operating Decision

The job currently uses manual execution to control portfolio-project cost. A scheduled trigger can be enabled later without redesigning the ETL runtime.

### Success Criteria

The job runs successfully in Azure, writes expected bronze and silver artifacts, and produces diagnosable execution logs.

---

## Milestone 7: GitHub Actions to Azure CI/CD — In Progress

### Objective

Build, publish, and deploy SignalWatch container changes to Azure from GitHub Actions using secure, repeatable authentication.

### Scope

- Configure GitHub-to-Azure OpenID Connect authentication
- Assign least-privilege Azure roles
- Retain pull-request linting and tests
- Build versioned ETL container images
- Push images to Azure Container Registry
- Update the Azure Container Apps Job image
- Add environment-specific GitHub configuration
- Add deployment verification and failure diagnostics
- Document rollback and manual deployment procedures
- Add API container deployment when the API cloud runtime is provisioned

### Deliverables

- Azure deployment workflow
- OIDC-based authentication
- Versioned ACR images
- Automated Container Apps Job update
- Deployment verification
- CI/CD runbook

### Success Criteria

- Pull requests run linting and tests
- Merges to `main` build a versioned image
- Images are pushed to ACR
- The Azure Container Apps Job is updated from GitHub Actions
- No long-lived Azure credential is stored in the repository
- A failed deployment is visible and recoverable

---

## Milestone 8: Snowflake Batch Load Integration — Planned

### Objective

Load curated SignalWatch outputs from ADLS into Snowflake for analytical querying.

### Scope

- Create Snowflake database, schemas, and warehouse
- Configure an Azure storage integration
- Create an external stage over the selected silver or gold path
- Define Parquet file formats and target tables
- Add idempotent `COPY INTO` batch loads
- Record load history
- Reconcile Snowflake counts with ADLS and PostgreSQL
- Document setup and operating procedures

### Success Criteria

Snowflake can securely access the configured ADLS path, load curated files, and reconcile the resulting data with upstream systems.

---

## Milestone 9: Snowflake Analytics Views — Planned

### Objective

Create documented analytical models that demonstrate why Snowflake exists in the architecture beyond the operational API.

### Scope

- Supply-chain event trend view
- Country and category aggregation view
- High-risk event view
- Source coverage view
- Pipeline load audit view
- Example analytical SQL and validation queries

### Success Criteria

Snowflake answers aggregate trend, risk, source-coverage, and load-audit questions through reusable documented views.

---

## Milestone 10: Snowpipe Auto-Ingest — Optional

### Objective

Evaluate continuous ingestion from Azure storage after the batch-loading model is stable.

### Scope

- Azure Event Grid integration
- Snowflake notification integration
- Snowpipe definition
- Auto-ingest monitoring
- Failure handling and troubleshooting documentation
- Cost and operational-value evaluation

### Success Criteria

New eligible files can trigger Snowflake loads, failed loads can be diagnosed, and the project documents whether auto-ingest provides enough value to retain.

---

## Milestone 11: Risk Scoring and Data Quality — Planned

### Objective

Add explainable intelligence and trust signals to the platform.

### Scope

- Rolling event-volume baselines
- Spike detection
- Explainable risk scores
- Risk score history
- Event uniqueness and range checks
- Freshness tracking
- Duplicate, null-location, and unmapped-code rates
- Persisted data-quality results
- Risk and quality API endpoints
- Tests for scoring and validation rules

### Success Criteria

The system detects abnormal activity, explains each risk score, and reports whether source and normalized data satisfy defined quality thresholds.

---

## Milestone 12: Watchlists and Alerts — Planned

### Objective

Allow users to monitor selected regions, topics, categories, and thresholds and generate explainable alerts when matching patterns occur.

### Scope

- Watchlist and watchlist-rule tables
- Watchlist CRUD API endpoints
- Rules by region, topic, category, and risk threshold
- Alert generation job
- Alert severity levels
- Alert explanation text
- Alert history
- Mock notification support
- Example watchlist configurations

### Success Criteria

A user can create a watchlist and receive an explainable stored alert when matching event patterns exceed a defined threshold.

---

## Milestone 13: Observability and Dashboard — Planned

### Objective

Make SignalWatch easy to operate and demonstrate.

### Scope

- Structured application and pipeline logging
- Service, API latency, ingestion, freshness, and failure metrics
- Operational health dashboard
- Current risk summary
- Event trend and regional hotspot views
- Alert feed
- Data-quality panel
- Source and event drill-down
- Operational runbook and demo walkthrough

### Success Criteria

An engineer can assess system health without manually reading raw logs, and a viewer can follow an end-to-end demo from ingestion through trends, risk, and alerts.

---

## Milestone 14: Evaluation and Project Hardening — Planned

### Objective

Evaluate alert usefulness, improve reliability, and finish the project as a credible engineering case study.

### Scope

- Small labeled alert-evaluation dataset
- False-positive and useful-alert review
- Known limitations and design tradeoffs
- Architecture and data-model diagrams
- Expanded operational runbooks
- Test-coverage improvements
- Security and cost review
- Repository cleanup
- Final README, screenshots, and demo materials
- Resume-ready project bullets

### Success Criteria

The project communicates what was built, why it was designed this way, how it is operated, how its outputs were evaluated, and what limitations remain.

---

## Current Build Order

1. Local Runtime Foundation — Complete
2. GDELT Raw Ingestion Workflow — Complete
3. Normalize and Persist GDELT Events — Complete
4. Event Query API — Complete
5. Azure Data Lake Storage Integration — Complete
6. Azure ETL Runtime — Complete
7. GitHub Actions to Azure CI/CD — In progress
8. Snowflake Batch Load Integration — Planned
9. Snowflake Analytics Views — Planned
10. Snowpipe Auto-Ingest — Optional
11. Risk Scoring and Data Quality — Planned
12. Watchlists and Alerts — Planned
13. Observability and Dashboard — Planned
14. Evaluation and Project Hardening — Planned

## Architecture Direction

```text
GDELT
  -> ETL worker
  -> ADLS bronze
  -> normalization
  -> PostgreSQL application tables + ADLS silver Parquet
  -> FastAPI event API
  -> Snowflake analytical layer
  -> risk scoring and data-quality results
  -> watchlists and alerts
  -> operational and user-facing dashboards
```

The ordering deliberately establishes durable storage, cloud execution, and deployment automation before adding warehouse analytics and higher-level product features.

## MVP and Portfolio Targets

### Current MVP Foundation

Milestones 1–7 provide the operated platform foundation: ingestion, normalization, application access, cloud storage, cloud execution, and CI/CD.

### Analytical MVP

Milestones 8, 9, and 11 add Snowflake analytics, explainable risk scoring, and data-quality reporting.

### Full Portfolio Project

Milestones 1–14 demonstrate backend engineering, data engineering, cloud/platform operations, CI/CD, warehouse integration, data quality, observability, evaluation, and product-oriented system design.
