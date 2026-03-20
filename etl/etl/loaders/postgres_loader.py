from dataclasses import dataclass

import pandas as pd
from psycopg2.extras import execute_values

from utils.db import get_cursor
from utils.logger import get_logger

logger = get_logger("postgres_loader")


@dataclass
class TableConfig:
    """Configuration d'insertion pour une table."""

    table: str
    columns: list[str]
    conflict_clause: str = ""


def _insert_rows(cur, table: str, columns: list[str], values: list[tuple], conflict_clause: str):
    """Insère les lignes et retourne le nombre réel d'insertions."""
    cols = ", ".join(columns)
    sql = f"INSERT INTO {table} ({cols}) VALUES %s {conflict_clause} RETURNING id"
    results = execute_values(cur, sql, values, page_size=1000, fetch=True)
    return len(results)


def load(df: pd.DataFrame, tables: list[TableConfig], source: str | None = None) -> int:
    """Charge un DataFrame dans une ou plusieurs tables PostgreSQL."""
    if df.empty:
        return 0

    df = df.copy()
    if source:
        df["source"] = source

    total = 0
    with get_cursor() as cur:
        for tc in tables:
            prep = df[tc.columns].astype(object).where(pd.notna(df[tc.columns]), None)
            values = list(prep.itertuples(index=False, name=None))
            inserted = _insert_rows(cur, tc.table, tc.columns, values, tc.conflict_clause)
            logger.info("Table %s : %d lignes insérées", tc.table, inserted)
            total += inserted

    return total
