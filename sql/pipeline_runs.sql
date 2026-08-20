CREATE TABLE IF NOT EXISTS pipeline_runs (
    id UUID PRIMARY KEY,
    pipeline_name TEXT NOT NULL,
    source_system TEXT NOT NULL,
    source_window_start TIMESTAMPTZ,
    source_window_end TIMESTAMPTZ,
    status TEXT NOT NULL,
    records_read INTEGER DEFAULT 0,
    records_written INTEGER DEFAULT 0,
    records_failed INTEGER DEFAULT 0,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMPTZ,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE pipeline_runs ADD COLUMN IF NOT EXISTS source_url TEXT;
ALTER TABLE pipeline_runs ADD COLUMN IF NOT EXISTS raw_output_path TEXT;
ALTER TABLE pipeline_runs ADD COLUMN IF NOT EXISTS file_size_bytes BIGINT;