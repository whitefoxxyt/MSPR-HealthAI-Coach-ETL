from datetime import datetime

import pandas as pd

from loaders.postgres_loader import load as pg_load
from pipelines import PIPELINES
from utils.db import log_etl_run
from utils.files import save_clean, save_quality_report, save_rejected, save_samples
from utils.logger import get_logger

logger = get_logger("etl")


def _quality_stats(clean: pd.DataFrame, rejected: pd.DataFrame) -> dict:
    """Calcule les statistiques de qualité depuis les DataFrames clean et rejected."""
    null_counts = {
        col: int(clean[col].isna().sum()) for col in clean.columns if clean[col].isna().any()
    }
    rejection_reasons = {}
    if not rejected.empty and "reason" in rejected.columns:
        rejection_reasons = rejected["reason"].value_counts().to_dict()
    return {"null_counts": null_counts, "rejection_reasons": rejection_reasons}


def run_pipeline(pipeline: dict) -> dict:
    """Orchestre extract, clean, export, load pour un pipeline donné."""
    name = pipeline["name"]
    started_at = datetime.now()
    rows_read = rows_inserted = rows_rejected = 0
    status = "OK"
    details: dict = {}

    try:
        raw = pipeline["extract"]()
        rows_read = len(raw)

        clean, rejected = pipeline["clean"](raw)
        rows_rejected = len(rejected)

        save_rejected(name, rejected)
        save_samples(name, raw, clean)
        save_clean(name, clean)

        table_counts = pg_load(clean, pipeline["tables"], pipeline.get("source"))
        rows_inserted = sum(table_counts.values())
        details["tables"] = table_counts
        details.update(_quality_stats(clean, rejected))

        logger.info("[%s] %d insérés, %d rejetés", name, rows_inserted, rows_rejected)

    except Exception as e:
        status = "ERREUR"
        details["error"] = str(e)
        logger.error("[%s] ERREUR : %s", name, e)

    finally:
        finished_at = datetime.now()
        details["duration_s"] = round((finished_at - started_at).total_seconds(), 3)
        log_etl_run(
            name, started_at, finished_at, rows_read, rows_inserted, rows_rejected, status, details
        )

    return {
        "name": name,
        "status": status,
        "rows_read": rows_read,
        "rows_inserted": rows_inserted,
        "rows_rejected": rows_rejected,
        "rejection_rate": round(rows_rejected / rows_read, 4) if rows_read else 0,
        "duration_s": details.get("duration_s"),
        "tables": details.get("tables", {}),
        "top_rejection_reasons": details.get("rejection_reasons", {}),
    }


if __name__ == "__main__":
    results = [run_pipeline(pipeline) for pipeline in PIPELINES]
    save_quality_report(results)
