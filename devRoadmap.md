# Development Roadmap

SignalWatch is organized around engineering milestones rather than fixed weekly delivery dates. Each milestone produces a usable increment of the platform and builds toward a complete, portfolio-ready system.

---

## Milestone 1: Project Foundation

### Objective
Create a clean, maintainable project foundation that supports local development, testing, and future cloud deployment.

### Scope
- Create the GitHub repository
- Set up the Python project structure
- Add FastAPI application skeleton
- Add Docker Compose
- Add PostgreSQL container
- Add test framework
- Add linting and formatting tools
- Define initial project conventions
- Draft the first README
- Define the initial normalized event schema

### Deliverables
- Running local API service
- Working Docker Compose environment
- Basic `/health` endpoint
- Initial test suite scaffold
- Initial project documentation

### Success Criteria
The project can be cloned, started locally, and verified through a passing health check and basic test command.

---

## Milestone 2: GDELT Ingestion Prototype

### Objective
Build the first working ingestion flow for retrieving GDELT data and storing ingestion metadata.

### Scope
- Implement a GDELT ingestion client
- Pull a defined GDELT event window
- Store raw source data locally or in object storage
- Create a `pipeline_runs` table
- Track ingestion start time, end time, status, and record counts
- Add retry handling
- Add structured logging
- Add basic checkpointing

### Deliverables
- Repeatable ingestion command
- Raw GDELT records persisted
- Pipeline run metadata stored
- Ingestion logs
- Tests for ingestion behavior

### Success Criteria
A developer can run one command that pulls a GDELT event window, stores the raw data, and records the pipeline run without manually editing state.

---

## Milestone 3: Normalized Event Model

### Objective
Transform raw GDELT records into clean, queryable internal event records.

### Scope
- Define normalized event tables
- Parse event timestamps
- Normalize country and location fields
- Extract actors, event codes, themes, and source URLs
- Map raw GDELT event codes to internal categories
- Add basic supply-chain domain classification
- Add deduplication logic
- Preserve lineage back to raw source files

### Deliverables
- Normalized event schema
- Transformation pipeline
- Queryable event records
- Category mapping logic
- Deduplication logic
- Unit tests for parsing and transformation

### Success Criteria
Raw GDELT data can be transformed into stable internal records that are easier to query and reason about than the source format.

---

## Milestone 4: Event Query API

### Objective
Expose normalized event data through a backend API.

### Scope
- Build `GET /events`
- Build `GET /events/{event_id}`
- Add filters for country, event category, domain, and time window
- Add pagination
- Add typed response models
- Add basic aggregate metadata
- Add `GET /pipeline/health`
- Add API tests
- Document example API requests

### Deliverables
- Searchable REST API
- Event detail endpoint
- Pipeline health endpoint
- API test coverage
- OpenAPI documentation

### Success Criteria
Users can query event records by geography, category, domain, and time window through documented API endpoints.

---

## Milestone 5: Trend Detection and Risk Scoring

### Objective
Create the first intelligence layer by detecting abnormal event activity and generating explainable risk scores.

### Scope
- Create event volume baselines
- Calculate rolling event counts
- Detect spikes against historical baselines
- Implement initial risk scoring
- Store risk score history
- Add explanation fields for each score
- Build `GET /risk/hotspots`
- Build `GET /risk/timeseries`

### Deliverables
- Risk scoring job
- Event baseline tables
- Hotspot endpoint
- Risk time-series endpoint
- Explainable scoring output
- Tests for scoring logic

### Success Criteria
The system can identify abnormal supply-chain-related event activity and explain why a region, topic, or category was flagged.

---

## Milestone 6: Watchlists and Alerts

### Objective
Allow users to define monitored topics and generate alerts when event patterns match those rules.

### Scope
- Create watchlist tables
- Add watchlist API endpoints
- Define watchlist rules by region, topic, category, and threshold
- Implement alert generation logic
- Add alert severity levels
- Add alert explanation text
- Store alert history
- Add mock notification support

### Deliverables
- Watchlist data model
- Watchlist API endpoints
- Alert generation job
- Alert history table
- Example watchlist configurations
- Example generated alerts

### Success Criteria
A user can create a watchlist and receive explainable alerts when matching event patterns exceed defined thresholds.

---

## Milestone 7: Data Quality Layer

### Objective
Add validation checks that make the platform more trustworthy and operationally realistic.

### Scope
- Add event uniqueness checks
- Validate timestamp ranges
- Validate latitude and longitude ranges
- Validate country codes when present
- Track source freshness
- Track duplicate rate
- Track null location rate
- Track unmapped event-code rate
- Store quality check results
- Expose data quality status through API

### Deliverables
- Data quality check framework
- `data_quality_results` table
- Freshness checks
- Duplicate-rate checks
- Null-rate checks
- Data quality API output
- Tests for validation rules

### Success Criteria
The platform can report whether the data is fresh, valid, and within expected quality thresholds.

---

## Milestone 8: Observability and Operational Health

### Objective
Make the platform observable like a real production system.

### Scope
- Add structured logging
- Add service metrics
- Add ingestion metrics
- Add API latency metrics
- Add pipeline failure metrics
- Add Prometheus support
- Add Grafana dashboard
- Add alerts for stale ingestion or repeated failures

### Deliverables
- Structured application logs
- Prometheus metrics endpoint
- Grafana dashboard
- Pipeline health dashboard
- Service health dashboard
- Operational runbook notes

### Success Criteria
An engineer can identify whether the system is healthy, whether ingestion is fresh, and whether failures are happening without reading raw logs manually.

---

## Milestone 9: Dashboard and Demo Experience

### Objective
Create a user-facing dashboard that clearly demonstrates the value of the system.

### Scope
- Build dashboard landing page
- Add current risk summary
- Add event trend visualization
- Add regional hotspot view
- Add alert feed
- Add source/event drill-down
- Add pipeline health panel
- Add data quality panel
- Add screenshots to README
- Write demo walkthrough

### Deliverables
- Working dashboard
- Risk summary view
- Event trend view
- Alert feed
- Pipeline health panel
- Data quality panel
- Demo script
- README screenshots

### Success Criteria
The project can be demonstrated end-to-end: ingest data, normalize events, query the API, detect risks, generate alerts, and show system health.

---

## Milestone 10: Cloud Deployment

### Objective
Deploy the platform to a real cloud environment with repeatable infrastructure.

### Scope
- Add Terraform configuration
- Provision cloud storage
- Provision database resources
- Deploy API container
- Deploy scheduled ingestion job
- Configure secrets management
- Configure environment variables
- Add CI/CD workflow
- Document deployment process

### Deliverables
- Cloud-hosted API
- Scheduled cloud ingestion job
- Infrastructure-as-code
- CI/CD pipeline
- Deployment documentation
- Environment configuration guide

### Success Criteria
The platform can be deployed from source control into a cloud environment using documented, repeatable steps.

---

## Milestone 11: Evaluation and Project Hardening

### Objective
Add evaluation, reliability improvements, and documentation that make the project credible as a portfolio case study.

### Scope
- Create a small labeled alert evaluation set
- Review false positives and useful alerts
- Document known limitations
- Document design tradeoffs
- Add architecture diagrams
- Add data model documentation
- Add operational runbook
- Improve test coverage
- Clean up repository issues
- Prepare resume bullets and case-study notes

### Deliverables
- Evaluation notes
- Known limitations section
- Architecture documentation
- Data model documentation
- Operational runbook
- Final README polish
- Resume-ready project bullets

### Success Criteria
The project clearly communicates not only what was built, but why it was designed that way, how it can be operated, and what its limitations are.

---

## Recommended Milestone Sets

### MVP Milestone Set
The minimum viable version of SignalWatch should include:

- Project foundation
- GDELT ingestion prototype
- Normalized event model
- Event query API
- Basic risk scoring
- Basic data freshness check

At that point, the project is already useful and demonstrable.

### Full Portfolio Milestone Set
The complete portfolio version should include:

- Project foundation
- GDELT ingestion
- Normalized event model
- Event query API
- Trend detection and risk scoring
- Watchlists and alerts
- Data quality layer
- Observability and operational health
- Dashboard and demo experience
- Cloud deployment
- Evaluation and project hardening

This full milestone set demonstrates backend engineering, data engineering, platform operations, observability, and product-oriented system design.

### Recommended Build Order

1. Foundation
2. Ingestion
3. Normalization
4. API
5. Risk Scoring
6. Watchlists and Alerts
7. Data Quality
8. Observability
9. Dashboard
10. Cloud Deployment
11. Evaluation and Polish

This order keeps the project grounded: prove the ingestion, transformation, and service layers before adding dashboard polish or advanced scoring.
Document deployment process
Deliverables
Cloud-hosted API
Scheduled cloud ingestion job
Infrastructure-as-code
CI/CD pipeline
Deployment documentation
Environment configuration guide
Success Criteria

The platform can be deployed from source control into a cloud environment using documented, repeatable steps.

Milestone 11: Evaluation and Project Hardening
Objective

Add evaluation, reliability improvements, and documentation that make the project credible as a portfolio case study.

Scope
Create a small labeled alert evaluation set
Review false positives and useful alerts
Document known limitations
Document design tradeoffs
Add architecture diagrams
Add data model documentation
Add operational runbook
Improve test coverage
Clean up repository issues
Prepare resume bullets and case-study notes
Deliverables
Evaluation notes
Known limitations section
Architecture documentation
Data model documentation
Operational runbook
Final README polish
Resume-ready project bullets
Success Criteria

The project clearly communicates not only what was built, but why it was designed that way, how it can be operated, and what its limitations are.

MVP Milestone Set

The minimum viable version of SignalWatch should include:

Project foundation
GDELT ingestion prototype
Normalized event model
Event query API
Basic risk scoring
Basic data freshness check

At that point, the project is already useful and demonstrable.

Full Portfolio Milestone Set

The complete portfolio version should include:

Project foundation
GDELT ingestion
Normalized event model
Event query API
Trend detection and risk scoring
Watchlists and alerts
Data quality layer
Observability and operational health
Dashboard and demo experience
Cloud deployment
Evaluation and project hardening

This full milestone set demonstrates backend engineering, data engineering, platform operations, observability, and product-oriented system design.

Recommended Build Order

The recommended order is:

Foundation
→ Ingestion
→ Normalization
→ API
→ Risk Scoring
→ Watchlists and Alerts
→ Data Quality
→ Observability
→ Dashboard
→ Cloud Deployment
→ Evaluation and Polish

This order keeps the project grounded. The platform should prove that it can reliably ingest, transform, and serve data before adding dashboard polish or advanced scoring.