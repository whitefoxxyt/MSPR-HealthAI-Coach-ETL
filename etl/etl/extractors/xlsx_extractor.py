import pandas as pd

from utils.logger import get_logger

logger = get_logger("xlsx_extractor")


def extract(
    path: str,
    required_columns: set[str] | None = None,
    *,
    sheet_name: str | int = 0,
) -> pd.DataFrame:
    """Extrait un fichier Excel dans un DataFrame."""
    df = pd.read_excel(path, sheet_name=sheet_name, engine="openpyxl")

    if required_columns:
        missing = required_columns - set(df.columns)
        if missing:
            raise ValueError(f"Colonnes manquantes dans {path} : {missing}")

    df = df.dropna(how="all").reset_index(drop=True)
    logger.info("XLSX %s (feuille=%s) : %d lignes extraites", path, sheet_name, len(df))
    return df
