import pandas as pd

from utils.cleaning import clean_text, require_non_empty

COLUMN_MAP = {
    "exerciseId": "external_id",
    "name": "name",
    "bodyParts": "body_parts",
    "targetMuscles": "target_muscles",
    "secondaryMuscles": "secondary_muscles",
    "equipments": "equipments",
    "instructions": "instructions",
    "gifUrl": "gif_url",
}


def clean(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Nettoie le catalogue d'exercices."""
    df = df.rename(columns=COLUMN_MAP).copy()

    valid = require_non_empty(df, "external_id") & require_non_empty(df, "name")

    df["name"] = df["name"].astype(str).str.strip()

    df["instructions"] = df["instructions"].apply(
        lambda x: "\n".join(x) if isinstance(x, list) and x else None
    )

    clean_text(df, ["gif_url"])

    for col in ["body_parts", "target_muscles", "secondary_muscles", "equipments"]:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: x if isinstance(x, list) else [])

    rejected = df[~valid].copy()
    rejected["reason"] = "exerciseId ou name manquant"

    return df[valid].reset_index(drop=True), rejected.reset_index(drop=True)
