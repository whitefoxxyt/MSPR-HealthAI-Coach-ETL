import csv

import pandas as pd

from utils.logger import get_logger

logger = get_logger("csv_extractor")


def extract(
    paths: str | list[str],
    required_columns: set[str] | None = None,
    *,
    food_name_quirk: bool = False,
) -> pd.DataFrame:
    """Extrait un ou plusieurs CSV dans un DataFrame unique."""
    if isinstance(paths, str):
        paths = [paths]

    frames: list[pd.DataFrame] = []
    for path in paths:
        if food_name_quirk:
            df = _extract_with_food_quirk(path, required_columns)
        else:
            df = _extract_standard(path, required_columns)
        frames.append(df)
        logger.info("CSV %s : %d lignes extraites", path, len(df))

    return pd.concat(frames, ignore_index=True) if len(frames) > 1 else frames[0]


def _extract_standard(path: str, required_columns: set[str] | None) -> pd.DataFrame:
    """Lecture CSV standard via pandas."""
    df = pd.read_csv(path, encoding="utf-8")
    _check_columns(df, path, required_columns)
    return df.dropna(how="all").reset_index(drop=True)


def _extract_with_food_quirk(path: str, required_columns: set[str] | None) -> pd.DataFrame:
    """Lecture CSV avec gestion des virgules dans la première colonne."""
    rows = []
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        _check_columns_from_list(header, path, required_columns)
        n = len(header)
        for parts in reader:
            if not parts or not any(v.strip() for v in parts):
                continue
            if len(parts) == n:
                rows.append(dict(zip(header, parts)))
            elif len(parts) > n:
                overflow = len(parts) - n
                food_name = ",".join(parts[: overflow + 1])
                rest = parts[overflow + 1 :]
                rows.append(dict(zip(header, [food_name] + rest)))
    return pd.DataFrame(rows)


def _check_columns(df: pd.DataFrame, path: str, required_columns: set[str] | None):
    if required_columns:
        missing = required_columns - set(df.columns)
        if missing:
            raise ValueError(f"Colonnes manquantes dans {path} : {missing}")


def _check_columns_from_list(header: list[str], path: str, required_columns: set[str] | None):
    if required_columns:
        missing = required_columns - set(header)
        if missing:
            raise ValueError(f"Colonnes manquantes dans {path} : {missing}")
