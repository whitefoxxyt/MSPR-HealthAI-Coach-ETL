import json

import pandas as pd

from utils.logger import get_logger

logger = get_logger("json_extractor")


def extract(path: str, required_columns: set[str] | None = None) -> pd.DataFrame:
    """Extrait un fichier JSON dans un DataFrame."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(f"Format inattendu : liste attendue, obtenu {type(data).__name__}")

    df = pd.DataFrame(data)

    if required_columns:
        missing = required_columns - set(df.columns)
        if missing:
            raise ValueError(f"Colonnes manquantes dans {path} : {missing}")

    logger.info("JSON %s : %d lignes extraites", path, len(df))
    return df
