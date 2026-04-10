from datetime import datetime

from loaders.postgres_loader import load as pg_load
from pipelines import PIPELINES
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


if __name__ == "__main__":
    for pipeline in PIPELINES:
        run_pipeline(pipeline)
