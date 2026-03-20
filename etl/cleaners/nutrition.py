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
    "Food_Item": "food_name",
    "Category": "category",
    "Meal_Type": "meal_type",
    "Calories (kcal)": "calories",
    "Protein (g)": "protein_g",
    "Carbohydrates (g)": "carbs_g",
    "Fat (g)": "fat_g",
    "Fiber (g)": "fiber_g",
    "Sugars (g)": "sugars_g",
    "Sodium (mg)": "sodium_mg",
    "Cholesterol (mg)": "cholesterol_mg",
    "Water_Intake (ml)": "water_ml",
}

NUMERIC_COLS = [
    "calories",
    "protein_g",
    "carbs_g",
    "fat_g",
    "fiber_g",
    "sugars_g",
    "sodium_mg",
    "cholesterol_mg",
    "water_ml",
]


def clean(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Nettoie les données nutritionnelles."""
    df = df.rename(columns=COLUMN_MAP).copy()

    to_numeric(df, NUMERIC_COLS)
    clean_text(df, ["category", "meal_type"])

    valid, reasons = init_validation(df)

    food_ok = require_non_empty(df, "food_name")
    reasons = reasons.where(food_ok, "food_name manquant")
    valid &= food_ok

    valid, reasons = check_bounds(df, [("calories", "calories")], valid, reasons)

    for col in ["protein_g", "carbs_g", "fat_g"]:
        if col in df.columns:
            df[col] = df[col].clip(lower=0)

    df["status"] = "NETTOYE"

    return split_valid_rejected(df, valid, reasons)
