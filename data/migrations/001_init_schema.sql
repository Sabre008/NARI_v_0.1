-- ============================================================
-- N.A.R.I — Initial Database Schema
-- DESIGN.md §4: Four core tables for the Supabase PostgreSQL DB
-- ============================================================
-- Run this in the Supabase SQL Editor to initialise the schema.

-- Enable PostGIS for geometry columns
CREATE EXTENSION IF NOT EXISTS postgis;

-- ── 1. users ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    user_id         UUID PRIMARY KEY,           -- From Supabase Auth
    gender          VARCHAR(10) NOT NULL,        -- 'male' or 'female'
    trust_score     FLOAT DEFAULT 1.0,           -- Anomaly-adjusted trust
    account_created TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE users IS 'User profiles with demographic data for M_demo and trust scoring.';

-- ── 2. locations_grid ───────────────────────────────────
CREATE TABLE IF NOT EXISTS locations_grid (
    centroid_id      BIGINT PRIMARY KEY,          -- H3 Hex Index
    geometry         GEOMETRY(Polygon, 4326),     -- Cell boundary polygon
    base_infra_score FLOAT DEFAULT 0.5,           -- S_infra from SafetyNet DNN
    poi_metadata     JSONB DEFAULT '{}'::JSONB    -- Raw feature counts
);

CREATE INDEX IF NOT EXISTS idx_grid_geometry
    ON locations_grid USING GIST (geometry);

COMMENT ON TABLE locations_grid IS 'H3 hexagonal grid cells with pre-computed infrastructure safety scores.';

-- ── 3. crowd_reports ────────────────────────────────────
CREATE TABLE IF NOT EXISTS crowd_reports (
    report_id   BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    centroid_id BIGINT NOT NULL REFERENCES locations_grid(centroid_id),
    user_id     UUID NOT NULL REFERENCES users(user_id),
    rating_score INT NOT NULL CHECK (rating_score BETWEEN 1 AND 5),
    timestamp   TIMESTAMPTZ DEFAULT NOW(),
    is_verified BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_reports_cell
    ON crowd_reports (centroid_id);
CREATE INDEX IF NOT EXISTS idx_reports_user
    ON crowd_reports (user_id);

COMMENT ON TABLE crowd_reports IS 'User-submitted safety ratings with Isolation Forest verification.';

-- ── 4. news_hazards ─────────────────────────────────────
CREATE TABLE IF NOT EXISTS news_hazards (
    incident_id    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    centroid_id    BIGINT NOT NULL REFERENCES locations_grid(centroid_id),
    severity_score FLOAT NOT NULL CHECK (severity_score BETWEEN 0 AND 1),
    expiry_timer   TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_hazards_cell
    ON news_hazards (centroid_id);
CREATE INDEX IF NOT EXISTS idx_hazards_expiry
    ON news_hazards (expiry_timer);

COMMENT ON TABLE news_hazards IS 'NLP-detected hazard incidents with automatic expiry.';
