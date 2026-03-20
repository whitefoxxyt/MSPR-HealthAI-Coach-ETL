from datetime import datetime

import pandas as pd

from generators import fake_users as user_generator
from loaders.postgres_loader import load as pg_load
from pipelines import PIPELINES
from pipelines.faker_users import COUNT, TABLE
from utils.db import log_etl_run
from utils.files import save_clean, save_rejected, save_samples
from utils.logger import get_logger

logger = get_logger("etl")


def run_pipeline(pipeline: dict):
    """Orchestre extract, clean, export, load pour un pipeline donné."""
    name = pipeline["name"]
    started_at = datetime.now()
    rows_read = rows_inserted = rows_rejected = 0
    status = "OK"
    details = None

    try:
        raw = pipeline["extract"]()
        rows_read = len(raw)

        clean, rejected = pipeline["clean"](raw)
        rows_rejected = len(rejected)

        save_rejected(name, rejected)
        save_samples(name, raw, clean)
        save_clean(name, clean)

        rows_inserted = pg_load(clean, pipeline["tables"], pipeline.get("source"))
        logger.info("[%s] %d insérés, %d rejetés", name, rows_inserted, rows_rejected)

    except Exception as e:
        status = "ERREUR"
        details = str(e)
        logger.error("[%s] ERREUR : %s", name, e)

    finally:
        finished_at = datetime.now()
        log_etl_run(
            name, started_at, finished_at, rows_read, rows_inserted, rows_rejected, status, details
        )


def run_faker_pipeline():
    """Génère des utilisateurs fictifs via Faker et les charge en base."""
    started_at = datetime.now()
    status = "OK"
    details = None
    rows_inserted = 0

    try:
        users = user_generator.generate(COUNT)
        df = pd.DataFrame(users)
        rows_inserted = pg_load(df, [TABLE])
        logger.info("[faker_users] %d utilisateurs insérés", rows_inserted)

    except Exception as e:
        status = "ERREUR"
        details = str(e)
        logger.error("[faker_users] ERREUR : %s", e)

    finally:
        finished_at = datetime.now()
        log_etl_run(
            "faker_users", started_at, finished_at, COUNT, rows_inserted, 0, status, details
        )


if __name__ == "__main__":
    for pipeline in PIPELINES:
        run_pipeline(pipeline)
    run_faker_pipeline()
