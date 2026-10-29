from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Any

import pandas as pd
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "employee_retention_analytics"),
    "connection_timeout": 8,
}

EXPECTED_TABLES = [
    "roles", "teams", "employees", "employee_role_history",
    "employee_team_history", "tenure_snapshots", "engagement_surveys",
    "workload_snapshots", "compensation_bands", "promotion_history",
    "attrition_outcomes", "interventions", "employee_lifecycle_events",
    "intervention_events",
]

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

@contextmanager
def connection_scope():
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()

def query_df(sql: str, params: tuple | list | None = None) -> pd.DataFrame:
    with connection_scope() as conn:
        return pd.read_sql(sql, conn, params=params)

def execute_sql(sql: str, params: tuple | list | None = None) -> int:
    with connection_scope() as conn:
        cur = conn.cursor()
        try:
            cur.execute(sql, params or ())
            conn.commit()
            return cur.rowcount
        finally:
            cur.close()

def list_tables() -> list[str]:
    df = query_df(
        "SELECT TABLE_NAME FROM information_schema.tables "
        "WHERE table_schema = %s ORDER BY TABLE_NAME",
        (DB_CONFIG["database"],),
    )
    return df["TABLE_NAME"].tolist() if not df.empty else []

def table_columns(table: str) -> list[str]:
    if table not in list_tables():
        return []
    df = query_df(
        "SELECT COLUMN_NAME FROM information_schema.columns "
        "WHERE table_schema=%s AND table_name=%s ORDER BY ORDINAL_POSITION",
        (DB_CONFIG["database"], table),
    )
    return df["COLUMN_NAME"].tolist() if not df.empty else []

def safe_count(table: str) -> int | None:
    if table not in list_tables():
        return None
    df = query_df(f"SELECT COUNT(*) AS n FROM `{table}`")
    return int(df.iloc[0]["n"]) if not df.empty else 0

def safe_sample(table: str, limit: int = 1000) -> pd.DataFrame:
    if table not in list_tables():
        return pd.DataFrame()
    return query_df(f"SELECT * FROM `{table}` LIMIT {int(limit)}")

def first_existing(columns: list[str], candidates: list[str]) -> str | None:
    lower_map = {c.lower(): c for c in columns}
    for candidate in candidates:
        if candidate.lower() in lower_map:
            return lower_map[candidate.lower()]
    return None

def get_metric_frame(table: str, date_candidates: list[str] | None = None) -> pd.DataFrame:
    """Fetch a bounded sample from a known table; used for schema-tolerant analysis."""
    if table not in list_tables():
        return pd.DataFrame()
    cols = table_columns(table)
    date_col = first_existing(cols, date_candidates or ["observation_date", "snapshot_date", "survey_date", "event_date", "created_at"])
    selected = [c for c in cols]
    if date_col and date_col in selected:
        # Keep all columns but limit volume; analytics pages aggregate this sample when needed.
        return query_df(f"SELECT * FROM `{table}` ORDER BY `{date_col}` DESC LIMIT 50000")
    return query_df(f"SELECT * FROM `{table}` LIMIT 50000")

def db_health() -> dict[str, Any]:
    try:
        tables = list_tables()
        counts = {t: safe_count(t) for t in EXPECTED_TABLES}
        return {"ok": True, "database": DB_CONFIG["database"], "tables": tables, "counts": counts, "error": None}
    except Exception as exc:
        return {"ok": False, "database": DB_CONFIG["database"], "tables": [], "counts": {}, "error": str(exc)}
