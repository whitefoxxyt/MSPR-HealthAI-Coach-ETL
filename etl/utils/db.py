import os
import threading
from contextlib import contextmanager

from psycopg2 import pool

from config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER
from utils.logger import get_logger

logger = get_logger("db")

_DB_POOL_MIN = int(os.environ.get("DB_POOL_MIN", "1"))
_DB_POOL_MAX = int(os.environ.get("DB_POOL_MAX", "5"))

_pool: pool.ThreadedConnectionPool | None = None
_pool_lock = threading.Lock()


def _get_pool() -> pool.ThreadedConnectionPool:
    global _pool
    if _pool is None:
        with _pool_lock:
            if _pool is None:
                _pool = pool.ThreadedConnectionPool(
                    minconn=_DB_POOL_MIN,
                    maxconn=_DB_POOL_MAX,
                    host=DB_HOST,
                    port=DB_PORT,
                    dbname=DB_NAME,
                    user=DB_USER,
                    password=DB_PASSWORD,
                )
                logger.info(
                    "Pool de connexions DB initialisé (min=%d, max=%d)", _DB_POOL_MIN, _DB_POOL_MAX
                )
    return _pool


@contextmanager
def get_cursor():
    db_pool = _get_pool()
    conn = db_pool.getconn()
    try:
        with conn.cursor() as cur:
            yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        db_pool.putconn(conn)


def log_etl_run(
    name, started_at, finished_at, rows_read, rows_inserted, rows_rejected, status, details=None
):
    """Écrit une entrée dans etl_logs."""
    try:
        with get_cursor() as cur:
            cur.execute(
                """
                INSERT INTO etl_logs
                    (source_name, started_at, finished_at,
                     rows_read, rows_inserted, rows_rejected, error_count, status, details)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    name,
                    started_at,
                    finished_at,
                    rows_read,
                    rows_inserted,
                    rows_rejected,
                    1 if status == "ERREUR" else 0,
                    status,
                    details,
                ),
            )
    except Exception as e:
        logger.error("[%s] Impossible d'écrire dans etl_logs : %s", name, e)
