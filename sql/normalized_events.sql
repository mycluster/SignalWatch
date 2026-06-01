CREATE TABLE normalized_events (
    id UUID PRIMARY KEY,

    -- Source lineage
    source_system TEXT NOT NULL DEFAULT 'GDELT',
    source_event_id TEXT NOT NULL,
    source_file_path TEXT,
    source_url TEXT,
    raw_record_hash TEXT NOT NULL,

    -- Event timing
    event_date DATE,
    event_timestamp TIMESTAMPTZ,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    normalized_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Location
    country_code TEXT,
    country_name TEXT,
    admin_region TEXT,
    city TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    geo_precision TEXT,

    -- Event classification
    event_code TEXT,
    event_root_code TEXT,
    event_category TEXT NOT NULL,
    event_subcategory TEXT,
    domain TEXT NOT NULL DEFAULT 'GENERAL',
    supply_chain_relevance_score NUMERIC(5, 2),

    -- Actors
    actor_1_name TEXT,
    actor_1_country_code TEXT,
    actor_1_type TEXT,
    actor_2_name TEXT,
    actor_2_country_code TEXT,
    actor_2_type TEXT,

    -- Signal attributes
    goldstein_score NUMERIC(6, 2),
    avg_tone NUMERIC(6, 2),
    source_count INTEGER,
    mention_count INTEGER,
    article_count INTEGER,

    -- Derived fields
    is_supply_chain_related BOOLEAN NOT NULL DEFAULT FALSE,
    confidence_score NUMERIC(5, 2),
    duplicate_group_id TEXT,

    -- Operational metadata
    pipeline_run_id UUID,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_source_event UNIQUE (source_system, source_event_id),
    CONSTRAINT ck_latitude CHECK (latitude IS NULL OR latitude BETWEEN -90 AND 90),
    CONSTRAINT ck_longitude CHECK (longitude IS NULL OR longitude BETWEEN -180 AND 180),
    CONSTRAINT ck_confidence_score CHECK (
        confidence_score IS NULL OR confidence_score BETWEEN 0 AND 100
    ),
    CONSTRAINT ck_supply_chain_relevance_score CHECK (
        supply_chain_relevance_score IS NULL OR supply_chain_relevance_score BETWEEN 0 AND 100
    )
);