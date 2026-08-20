CREATE TABLE IF NOT EXISTS normalized_events (
    id UUID PRIMARY KEY,

    source_system TEXT NOT NULL DEFAULT 'GDELT',
    source_event_id TEXT NOT NULL,
    source_file_path TEXT,
    source_url TEXT,
    raw_record_hash TEXT NOT NULL,

    event_date DATE,
    event_timestamp TIMESTAMPTZ,

    country_code TEXT,
    country_name TEXT,
    admin_region TEXT,
    city TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    geo_precision TEXT,

    event_code TEXT,
    event_root_code TEXT,
    event_category TEXT NOT NULL,
    event_subcategory TEXT,
    domain TEXT NOT NULL DEFAULT 'GENERAL',

    actor_1_name TEXT,
    actor_1_country_code TEXT,
    actor_1_type TEXT,
    actor_2_name TEXT,
    actor_2_country_code TEXT,
    actor_2_type TEXT,

    goldstein_score NUMERIC(6, 2),
    avg_tone NUMERIC(6, 2),
    source_count INTEGER,
    mention_count INTEGER,
    article_count INTEGER,

    is_supply_chain_related BOOLEAN NOT NULL DEFAULT FALSE,
    supply_chain_relevance_score NUMERIC(5, 2),
    confidence_score NUMERIC(5, 2),

    pipeline_run_id UUID,
    ingested_at TIMESTAMPTZ,
    normalized_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_normalized_events_source UNIQUE (source_system, source_event_id),
    CONSTRAINT ck_latitude CHECK (latitude IS NULL OR latitude BETWEEN -90 AND 90),
    CONSTRAINT ck_longitude CHECK (longitude IS NULL OR longitude BETWEEN -180 AND 180)
);

CREATE INDEX IF NOT EXISTS idx_normalized_events_timestamp
ON normalized_events (event_timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_normalized_events_country_time
ON normalized_events (country_code, event_timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_normalized_events_category_time
ON normalized_events (event_category, event_timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_normalized_events_domain_time
ON normalized_events (domain, event_timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_normalized_events_pipeline_run
ON normalized_events (pipeline_run_id);
