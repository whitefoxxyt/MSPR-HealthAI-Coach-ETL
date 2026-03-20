import os
import sys

import psycopg2

try:
    conn = psycopg2.connect(
        host=os.environ.get("DB_HOST", "db"),
        port=int(os.environ.get("DB_PORT", "5432")),
        dbname=os.environ.get("DB_NAME", "healthcoach"),
        user=os.environ.get("DB_USER", "healthcoach"),
        password=os.environ.get("DB_PASSWORD", "healthcoach"),
    )
    conn.close()
    sys.exit(0)
except Exception:
    sys.exit(1)
