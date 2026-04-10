import os
import sys


def _require(name: str, default: str) -> str:
    value = os.environ.get(name, default)
    if not value:
        print(
            f"[config] Variable d'environnement requise manquante ou vide : {name}", file=sys.stderr
        )
        sys.exit(1)
    return value


DB_HOST = _require("DB_HOST", "mspr-healthai-db")
DB_PORT = int(os.environ.get("DB_PORT", "5432") or "5432")
DB_NAME = _require("DB_NAME", "healthai")
DB_USER = _require("DB_USER", "healthai_user")
DB_PASSWORD = _require("DB_PASSWORD", "password")

DATA_DIR = os.environ.get("DATA_DIR", "/app/data/raw")
PROCESSED_DIR = os.environ.get("PROCESSED_DIR", "/app/data/processed")
SAMPLES_DIR = os.environ.get("SAMPLES_DIR", "/app/data/samples")

EXERCISES_JSON = os.path.join(DATA_DIR, "exercisedb", "exercises.json")
NUTRITION_CSV = os.path.join(DATA_DIR, "daily_food_nutrition_dataset.csv")
GYM_TRACKING_CSVS = [
    os.path.join(DATA_DIR, "gym_members_exercise_tracking.csv"),
    os.path.join(DATA_DIR, "gym_members_exercise_tracking_synthetic_data.csv"),
]
DIET_RECOMMENDATIONS_CSV = os.path.join(DATA_DIR, "diet_recommendations_dataset.csv")
