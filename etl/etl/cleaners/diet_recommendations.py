import pandas as pd

from utils.cleaning import (
    check_bounds,
    clean_text,
    init_validation,
    require_non_empty,
    split_valid_rejected,
    to_numeric,
)

COLUMN_MAP = {
    "Patient_ID": "external_patient_id",
    "Age": "age",
    "Gender": "gender",
    "Weight_kg": "weight_kg",
    "Height_cm": "height_cm",
    "BMI": "bmi",
    "Disease_Type": "disease_type",
    "Severity": "severity",
    "Physical_Activity_Level": "physical_activity_level",
    "Daily_Caloric_Intake": "daily_caloric_intake",
    "Cholesterol_mg/dL": "cholesterol_mg_dl",
    "Blood_Pressure_mmHg": "blood_pressure_mmhg",
    "Glucose_mg/dL": "glucose_mg_dl",
    "Dietary_Restrictions": "dietary_restrictions",
    "Allergies": "allergies",
    "Preferred_Cuisine": "preferred_cuisine",
    "Weekly_Exercise_Hours": "weekly_exercise_hours",
    "Adherence_to_Diet_Plan": "adherence_to_diet_plan",
    "Dietary_Nutrient_Imbalance_Score": "nutrient_imbalance_score",
    "Diet_Recommendation": "diet_recommendation",
}

NUMERIC_COLS = [
    "weight_kg",
    "height_cm",
    "bmi",
    "daily_caloric_intake",
    "cholesterol_mg_dl",
    "blood_pressure_mmhg",
    "glucose_mg_dl",
    "weekly_exercise_hours",
    "adherence_to_diet_plan",
    "nutrient_imbalance_score",
]

STR_COLS = [
    "gender",
    "disease_type",
    "severity",
    "physical_activity_level",
    "dietary_restrictions",
    "allergies",
    "preferred_cuisine",
    "diet_recommendation",
]

BOUNDS_CHECKS = [
    ("weight_kg", "weight_kg"),
    ("height_cm", "height_cm"),
    ("bmi", "bmi"),
]


def clean(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Nettoie les recommandations diététiques."""
    df = df.rename(columns=COLUMN_MAP).copy()

    to_numeric(df, NUMERIC_COLS)
    clean_text(df, STR_COLS)

    if "age" in df.columns:
        df["age"] = pd.to_numeric(df["age"], errors="coerce").round().astype("Int64")

    valid, reasons = init_validation(df)

    pid_ok = require_non_empty(df, "external_patient_id")
    reasons = reasons.where(pid_ok, "Patient_ID manquant")
    valid &= pid_ok

    valid, reasons = check_bounds(df, BOUNDS_CHECKS, valid, reasons)

    return split_valid_rejected(df, valid, reasons)
