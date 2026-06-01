# SignalWatch

**GDELT-Powered Supply Chain Risk Monitoring Platform**

SignalWatch is a production-style data platform that ingests global event data from GDELT, normalizes noisy public records, detects supply-chain disruption signals, and surfaces those signals through APIs, dashboards, alerts, and observability tooling.

This project demonstrates full-stack engineering judgment across backend development, data pipelines, cloud/platform operations, data quality, evaluation, and observability. It is designed as a realistic internal platform that turns frequently updated public event data into an explainable operational intelligence product.

---

## Problem Statement

Global public event data is abundant but difficult to use directly. Raw event feeds are often:

- Noisy
- Duplicated
- Inconsistently categorized
- Difficult to search
- Difficult to trust without quality checks
- Hard to operationalize without alerts, scoring, and context

Organizations that depend on global operations, logistics, or supply chains need more than raw news and event feeds. They need reliable signals, clear explanations, and confidence indicators.

SignalWatch addresses this by ingesting GDELT event data, applying normalization and validation, detecting abnormal activity, and surfacing supply-chain-related risk signals through APIs and dashboards.

---

## Project Goals

The project is designed to demonstrate:

- Incremental data ingestion
- Raw-to-curated data modeling
- Backend API design
- Scheduled jobs and checkpointing
- Data quality validation
- Risk scoring and trend detection
- Observability and pipeline monitoring
- Cloud-ready architecture
- Infrastructure-as-code
- Portfolio-quality system design documentation

---

## Local Development

Create a virtual environment and install the project with development tools:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

For a requirements-file based setup, use:

```powershell
python -m pip install -r requirements.txt
```

Docker Compose requires Docker Desktop or another Docker Engine installation available on your PATH.

Run the FastAPI app:

```powershell
uvicorn signalwatch.main:app --reload
```

Start PostgreSQL:

```powershell
docker compose up -d postgres
```

The default local database connection is:

```text
postgresql://signalwatch:signalwatch@localhost:5432/signalwatch
```

Verify the service:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health
```

Run tests and linting:

```powershell
pytest
ruff check .
```

Stop local containers:

```powershell
docker compose down
```

---

## Use Case

The initial use case is supply-chain disruption monitoring.

SignalWatch monitors event signals related to:

- Labor strikes
- Protests
- Port disruption
- Border closures
- Transportation delays
- Fuel shortages
- Civil unrest
- Natural disasters
- Conflict near logistics corridors
- Negative media trends around infrastructure or trade activity

Example questions the platform should answer:

- Are protest-related transportation events increasing in a specific region?
- Which countries are showing abnormal supply-chain-related activity?
- Are there event spikes near major ports or logistics hubs?
- What sources explain a generated alert?
- Is the underlying data fresh and trustworthy?

---

## High-Level Architecture

```text
GDELT Event Data
      ↓
Scheduled Ingestion Job
      ↓
Raw Data Storage
      ↓
Normalization Pipeline
      ↓
Data Quality Checks
      ↓
Curated Event Tables
      ↓
Risk Scoring and Trend Detection
      ↓
API Layer
      ↓
Dashboard, Watchlists, Alerts, Observability
```

---

## System Components

### 1. Ingestion Service

The ingestion service is responsible for pulling GDELT data on a recurring schedule.

**Responsibilities:**

- Pull GDELT event data
- Track processed time windows
- Support retries
- Handle failed runs
- Store raw records
- Maintain ingestion checkpoints
- Record pipeline metadata

**Key design requirement:**

Ingestion must be idempotent. Reprocessing the same window should not create duplicate business records or corrupt downstream state.

### 2. Raw Storage Layer

Raw GDELT records are stored before transformation.

**Purpose:**

- Preserve source data
- Support replay and reprocessing
- Improve debugging
- Maintain lineage
- Separate ingestion from transformation

**Example layout:**

```text
/raw/gdelt/events/year=2026/month=05/day=29/hour=14/
/raw/gdelt/events/year=2026/month=05/day=29/hour=15/
```

### 3. Normalization Pipeline

The normalization pipeline converts raw records into clean internal event models.

**Responsibilities:**

- Parse timestamps
- Normalize country/location fields
- Map raw event codes to internal categories
- Extract actors and themes
- Parse source URLs
- Deduplicate records
- Preserve lineage to raw source data

**Example normalized event:**

```json
{
  "event_id": "gdelt-20260529143000-123456",
  "event_time": "2026-05-29T14:30:00Z",
  "country_code": "FR",
  "region": "Île-de-France",
  "city": "Paris",
  "latitude": 48.8566,
  "longitude": 2.3522,
  "event_category": "PROTEST",
  "domain": "SUPPLY_CHAIN",
  "themes": ["labor", "transport", "strike"],
  "actors": ["transport workers", "labor union"],
  "tone": -4.2,
  "source_urls": ["https://example.com/article"],
  "created_at": "2026-05-29T14:45:00Z"
}
```

### 4. Data Quality Layer

Data quality checks are stored as first-class records.

**Example checks:**

- Event ID must be unique
- Event timestamp cannot be in the future
- Latitude must be between -90 and 90
- Longitude must be between -180 and 180
- Country code must be valid when present
- Source URL should be valid when present
- Duplicate rate should remain within expected bounds
- Null location rate should not spike unexpectedly
- Latest processed GDELT window should stay fresh

**Example quality result:**

```text
check_name: latest_window_freshness
status: failed
severity: high
measured_value: 97 minutes
expected_value: less than 30 minutes
```

### 5. Risk Scoring Layer

The risk scoring layer identifies abnormal supply-chain-related activity.

**Initial scoring factors:**

- Recent event volume
- Change from historical baseline
- Event severity
- Negative tone
- Source diversity
- Geographic relevance
- Persistence across time windows

**Example scoring model:**

```text
Risk Score =
  30% volume spike score
  20% event severity score
  15% source diversity score
  15% geographic relevance score
  10% tone score
  10% persistence score
```

Every score should include an explanation.

---

## Notes

SignalWatch is intended to be more than a simple dashboard. It is a platform that makes public event data actionable, explainable, and trustworthy for supply-chain risk operations.
Risk Score: 74
Severity: Medium

Why this was flagged:
- Protest-related transportation events are 3.2x above the 30-day baseline
- Events are concentrated near major logistics regions
- Multiple sources mention labor and transportation disruption
- Average media tone is significantly negative
API Design

Initial endpoints:

GET /health
GET /pipeline/health
GET /events
GET /events/{event_id}
GET /risk/hotspots
GET /risk/timeseries
GET /alerts
POST /watchlists
GET /watchlists
GET /watchlists/{watchlist_id}

Example request:

GET /events?domain=supply_chain&country=FR&event_category=PROTEST&since=24h

Example response:

{
  "count": 184,
  "window": "24h",
  "events": [],
  "aggregates": {
    "top_countries": ["FR", "DE", "BE"],
    "top_themes": ["labor", "transport", "fuel"],
    "average_tone": -3.8
  },
  "quality": {
    "freshness_minutes": 18,
    "deduplication_rate": 0.22,
    "source_coverage": "normal"
  }
}
Dashboard Concept

The dashboard should provide a clear operational view.

Recommended sections:

Current supply-chain risk summary
Regional event map
Event volume trend
Emerging topics
Active alerts
Source article drill-down
Pipeline health
Data quality status

Example dashboard summary:

Supply Chain Risk: Elevated

Reason:
Protest-related transport events in Western Europe are 3.4x above the 30-day baseline.

Freshness:
Last event window processed 17 minutes ago.

Confidence:
Medium. High event volume, moderate source diversity, and consistent negative tone.
Proposed Tech Stack
Local-First Version

This version should be built first.

Python
FastAPI
PostgreSQL
DuckDB
Docker Compose
Prefect or Dagster
SQLModel or SQLAlchemy
Pytest
Prometheus
Grafana
Streamlit or React
GitHub Actions
Cloud-Ready Version

This version can be added after the local platform works.

Azure Container Apps or AWS ECS
Azure Data Lake Storage or AWS S3
Databricks or Spark
PostgreSQL
Terraform
GitHub Actions
OpenTelemetry
Grafana
Cloud-native secrets management
Suggested Repository Structure
signalwatch/
  README.md
  docker-compose.yml
  pyproject.toml
  .github/
    workflows/
      ci.yml

  apps/
    api/
      main.py
      routes/
      models/
      services/

    dashboard/
      app.py

  pipelines/
    ingestion/
      gdelt_client.py
      ingest_events.py
      checkpoints.py

    transforms/
      normalize_events.py
      deduplicate.py
      map_event_categories.py

    quality/
      checks.py
      validators.py

    scoring/
      risk_score.py
      baselines.py
      alerts.py

  db/
    migrations/
    seed/
    models.py

  infra/
    terraform/

  observability/
    prometheus/
    grafana/

  tests/
    unit/
    integration/

  docs/
    architecture.md
    data-model.md
    evaluation.md
    limitations.md
