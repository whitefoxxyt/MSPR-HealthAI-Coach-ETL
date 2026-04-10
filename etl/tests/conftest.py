import os

import psycopg2
import pytest

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS exercises (
    id BIGSERIAL PRIMARY KEY,
    external_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    body_parts TEXT[],
    target_muscles TEXT[],
    secondary_muscles TEXT[],
    equipments TEXT[],
    instructions TEXT,
    gif_url VARCHAR(500),
    source VARCHAR(50) NOT NULL DEFAULT 'EXERCISEDB',
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS etl_logs (
    id BIGSERIAL PRIMARY KEY,
    source_name VARCHAR(100) NOT NULL,
    started_at TIMESTAMP NOT NULL,
    finished_at TIMESTAMP,
    rows_read INTEGER NOT NULL DEFAULT 0,
    rows_inserted INTEGER NOT NULL DEFAULT 0,
    rows_rejected INTEGER NOT NULL DEFAULT 0,
    error_count INTEGER NOT NULL DEFAULT 0,
    status VARCHAR(20) NOT NULL,
    details JSONB
);
"""


@pytest.fixture(scope="session")
def pg_conn():
    conn = psycopg2.connect(
        host=os.environ.get("DB_HOST", "db"),
        port=int(os.environ.get("DB_PORT", 5432)),
        dbname=os.environ.get("DB_NAME", "healthcoach"),
        user=os.environ.get("DB_USER", "healthcoach"),
        password=os.environ.get("DB_PASSWORD", "healthcoach"),
    )
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(SCHEMA_SQL)
    yield conn
    conn.close()


@pytest.fixture(autouse=False)
def clean_tables(pg_conn):
    yield
    with pg_conn.cursor() as cur:
        cur.execute("TRUNCATE exercises, etl_logs RESTART IDENTITY CASCADE")
