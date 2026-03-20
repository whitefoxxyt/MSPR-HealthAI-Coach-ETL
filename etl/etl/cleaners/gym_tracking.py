import pandas as pd

from utils.cleaning import (
    check_bounds,
    init_validation,
    require_non_empty,
    split_valid_rejected,
    to_numeric,
)

NUMERIC_COLS = [
    "Session_Duration (hours)",
    "Calories_Burned",
    "Weight (kg)",
    "Height (m)",
    "BMI",
    "Fat_Percentage",
    "Avg_BPM",
    "Max_BPM",
    "Resting_BPM",
]

BOUNDS_CHECKS = [
    ("weight_kg", "weight_kg"),
    ("height_cm", "height_cm"),
    ("bmi", "bmi"),
    ("fat_percentage", "fat_percentage"),
    ("duration_min", "duration_min"),
    ("heart_rate_avg", "heart_rate"),
    ("heart_rate_max", "heart_rate"),
    ("heart_rate_rest", "heart_rate"),
]


def clean(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Nettoie les données gym tracking (exercise + biometric)."""
    df = df.copy()

    to_numeric(df, NUMERIC_COLS)

    df["duration_min"] = (df["Session_Duration (hours)"] * 60).round(2)
    df["height_cm"] = (df["Height (m)"] * 100).round(1)

    df = df.rename(
        columns={
            "Workout_Type": "workout_type",
            "Calories_Burned": "calories_burned",
            "Weight (kg)": "weight_kg",
            "BMI": "bmi",
            "Fat_Percentage": "fat_percentage",
            "Avg_BPM": "heart_rate_avg",
            "Max_BPM": "heart_rate_max",
            "Resting_BPM": "heart_rate_rest",
        }
    )

    for col in ["heart_rate_avg", "heart_rate_max", "heart_rate_rest"]:
        df[col] = df[col].round().astype("Int64")

    valid, reasons = init_validation(df)

    wt_ok = require_non_empty(df, "workout_type")
    reasons = reasons.where(wt_ok, "Workout_Type manquant")
    valid &= wt_ok

    valid, reasons = check_bounds(df, BOUNDS_CHECKS, valid, reasons)

    df["status"] = "NETTOYE"

    return split_valid_rejected(df, valid, reasons)
