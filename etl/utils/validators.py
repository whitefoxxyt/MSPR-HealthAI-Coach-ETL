import pandas as pd

BOUNDS = {
    "calories": (0, 10_000),
    "weight_kg": (20, 300),
    "height_cm": (50, 250),
    "bmi": (10, 80),
    "heart_rate": (30, 250),
    "fat_percentage": (2, 70),
    "duration_min": (0, 480),
}


def validate_range(
    value, min_val: float, max_val: float, field_name: str
) -> tuple[object, str | None]:
    """Vérifie qu'une valeur est dans l'intervalle [min_val, max_val].

    Retourne ``(value, None)`` si valide ou ``(None, raison)`` si invalide.
    Les valeurs ``None`` passent sans vérification.
    """
    if value is None:
        return value, None
    if not (min_val <= value <= max_val):
        return None, f"{field_name} hors bornes ({value} pas dans [{min_val}, {max_val}])"
    return value, None


def validate_bounds(df: pd.DataFrame, column: str, bounds_key: str) -> pd.Series:
    """
    True si la valeur est dans BOUNDS[bounds_key] ou NaN.
    """
    lo, hi = BOUNDS[bounds_key]
    return df[column].isna() | df[column].between(lo, hi)
