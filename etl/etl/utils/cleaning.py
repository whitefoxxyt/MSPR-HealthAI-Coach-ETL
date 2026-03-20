import pandas as pd

from utils.validators import validate_bounds


def to_numeric(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Convertit les colonnes en numérique, NaN si invalide."""
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def clean_text(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Strip + remplace les valeurs vides/None/NaN par None."""
    for col in columns:
        if col in df.columns:
            s = df[col].astype(str).str.strip()
            df[col] = s.where(~s.str.lower().isin(["none", "", "nan"]), None)
    return df


def require_non_empty(df: pd.DataFrame, column: str) -> pd.Series:
    """Retourne True pour les lignes où la colonne est non vide."""
    return df[column].notna() & df[column].astype(str).str.strip().ne("")


def check_bounds(
    df: pd.DataFrame,
    bounds_checks: list[tuple[str, str]],
    valid: pd.Series,
    reasons: pd.Series,
) -> tuple[pd.Series, pd.Series]:
    """Valide plusieurs colonnes contre BOUNDS, accumule les raisons de rejet."""
    for col, key in bounds_checks:
        col_ok = validate_bounds(df, col, key)
        reasons = reasons.where(col_ok, reasons + f"; {col} hors bornes")
        valid &= col_ok
    return valid, reasons


def split_valid_rejected(
    df: pd.DataFrame, valid: pd.Series, reasons: pd.Series
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Sépare les lignes valides des rejetées avec la raison."""
    rejected = df[~valid].copy()
    rejected["reason"] = reasons[~valid].str.lstrip("; ")
    return df[valid].reset_index(drop=True), rejected.reset_index(drop=True)


def init_validation(df: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    """Initialise les masques de validation."""
    return pd.Series(True, index=df.index), pd.Series("", index=df.index)
