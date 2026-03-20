import math


def to_float(value) -> float | None:
    """Convertit une valeur en flottant, ou retourne None si la conversion échoue."""
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return None
    try:
        f = float(value)
        return None if math.isnan(f) else f
    except (ValueError, TypeError):
        return None


def to_int(value) -> int | None:
    """Convertit une valeur en entier, ou retourne None si la conversion échoue."""
    f = to_float(value)
    return None if f is None else round(f)


def str_or_none(value: str | None) -> str | None:
    """Retourne None si la valeur est absente, vide ou littéralement 'None'."""
    if not value:
        return None
    stripped = value.strip()
    return None if stripped.lower() == "none" else stripped
