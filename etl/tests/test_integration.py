"""Tests d'intégration — nécessitent PostgreSQL (service db)."""

from datetime import datetime
from unittest.mock import patch

import pandas as pd
import pytest

from loaders.postgres_loader import TableConfig, load
from main import run_pipeline
from utils.db import log_etl_run

pytestmark = pytest.mark.integration

EXERCISES_TABLE = TableConfig(
    table="exercises",
    columns=[
        "external_id",
        "name",
        "body_parts",
        "target_muscles",
        "secondary_muscles",
        "equipments",
        "instructions",
        "gif_url",
    ],
    conflict_clause="ON CONFLICT (external_id) DO NOTHING",
)


def _exercise_df(external_id="ex001"):
    return pd.DataFrame(
        [
            {
                "external_id": external_id,
                "name": "Push Up",
                "body_parts": ["chest"],
                "target_muscles": ["pectorals"],
                "secondary_muscles": ["triceps"],
                "equipments": ["body weight"],
                "instructions": "Step 1\nStep 2",
                "gif_url": "https://example.com/pushup.gif",
            }
        ]
    )


class TestPostgresLoader:
    def test_load_inserts_rows(self, pg_conn, clean_tables):
        inserted = load(_exercise_df(), [EXERCISES_TABLE])

        assert inserted == 1
        with pg_conn.cursor() as cur:
            cur.execute("SELECT external_id FROM exercises WHERE external_id = 'ex001'")
            assert cur.fetchone() is not None

    def test_load_is_idempotent(self, pg_conn, clean_tables):
        load(_exercise_df(), [EXERCISES_TABLE])
        inserted_second = load(_exercise_df(), [EXERCISES_TABLE])

        assert inserted_second == 0
        with pg_conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM exercises")
            assert cur.fetchone()[0] == 1

    def test_load_empty_df_returns_zero(self, pg_conn, clean_tables):
        inserted = load(pd.DataFrame(), [EXERCISES_TABLE])
        assert inserted == 0


class TestLogEtlRun:
    def test_writes_entry_to_etl_logs(self, pg_conn, clean_tables):
        now = datetime.now()
        log_etl_run(
            "test_pipeline", now, now, rows_read=10, rows_inserted=8, rows_rejected=2, status="OK"
        )

        with pg_conn.cursor() as cur:
            cur.execute(
                "SELECT source_name, rows_read, status FROM etl_logs WHERE source_name = 'test_pipeline'"
            )
            row = cur.fetchone()

        assert row == ("test_pipeline", 10, "OK")


class TestRunPipeline:
    def test_success_writes_log_and_inserts_data(self, pg_conn, clean_tables):
        raw_df = pd.DataFrame(
            [
                {
                    "exerciseId": "ex999",
                    "name": "Squat",
                    "bodyParts": ["legs"],
                    "targetMuscles": ["quadriceps"],
                    "secondaryMuscles": [],
                    "equipments": [],
                    "instructions": ["Step 1"],
                    "gifUrl": "",
                }
            ]
        )

        pipeline = {
            "name": "test_exercisedb",
            "extract": lambda: raw_df,
            "clean": __import__("cleaners.exercises", fromlist=["clean"]).clean,
            "tables": [EXERCISES_TABLE],
            "source": None,
        }

        with patch("main.save_rejected"), patch("main.save_samples"), patch("main.save_clean"):
            run_pipeline(pipeline)

        with pg_conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM exercises WHERE external_id = 'ex999'")
            assert cur.fetchone()[0] == 1

            cur.execute("SELECT status FROM etl_logs WHERE source_name = 'test_exercisedb'")
            assert cur.fetchone()[0] == "OK"
