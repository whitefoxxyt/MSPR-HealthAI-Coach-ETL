import json
import os
from datetime import datetime

import pandas as pd

from config import PROCESSED_DIR, SAMPLES_DIR
from utils.logger import get_logger

logger = get_logger("files")


def save_rejected(name: str, rejected: pd.DataFrame):
    """Sauvegarde les lignes rejetées en JSON."""
    if rejected.empty:
        return
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    path = os.path.join(PROCESSED_DIR, f"{name}_rejected.json")
    rejected.to_json(path, orient="records", force_ascii=False, indent=2)
    logger.info("[%s] %d rejets → %s", name, len(rejected), path)


def save_clean(name: str, df: pd.DataFrame):
    """Exporte les données nettoyées en CSV dans data/processed/."""
    if df.empty:
        return
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    path = os.path.join(PROCESSED_DIR, f"{name}_clean.csv")
    df.to_csv(path, index=False, encoding="utf-8")
    logger.info("[%s] %d lignes nettoyées → %s", name, len(df), path)


def save_samples(name: str, raw: pd.DataFrame, clean: pd.DataFrame, n: int = 5):
    """Exporte un échantillon brut + nettoyé en JSON dans data/samples/."""
    os.makedirs(SAMPLES_DIR, exist_ok=True)

    if not raw.empty:
        raw_path = os.path.join(SAMPLES_DIR, f"{name}_raw_sample.json")
        raw.head(n).to_json(raw_path, orient="records", force_ascii=False, indent=2)

    if not clean.empty:
        clean_path = os.path.join(SAMPLES_DIR, f"{name}_clean_sample.json")
        clean.head(n).to_json(clean_path, orient="records", force_ascii=False, indent=2)

    logger.info("[%s] samples (%d lignes) → %s", name, n, SAMPLES_DIR)


def save_quality_report(results: list[dict]):
    """Génère un rapport de qualité JSON global post-ETL dans data/processed/."""
    if not results:
        return
    rows_read_total = sum(r["rows_read"] for r in results)
    report = {
        "generated_at": datetime.now().isoformat(),
        "pipelines": results,
        "totals": {
            "rows_read": rows_read_total,
            "rows_inserted": sum(r["rows_inserted"] for r in results),
            "rows_rejected": sum(r["rows_rejected"] for r in results),
            "rejection_rate": round(
                sum(r["rows_rejected"] for r in results) / rows_read_total, 4
            )
            if rows_read_total
            else 0,
        },
    }
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    path = os.path.join(PROCESSED_DIR, "quality_report.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)
    logger.info("Rapport qualité → %s", path)
