'''
Database helpers: engine, connection helpers, reflection helpers, and migration tracking.
This module centralizes SQLite engine creation, PRAGMA setup (foreign keys),
and provides convenience functions to reflect table metadata and inspect existing columns.
'''
import datetime
import sqlite3
from typing import List, Dict
from sqlalchemy import create_engine, event, MetaData, Table, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError
DB_URL = "sqlite:///academic.db"
engine: Engine = create_engine(
    DB_URL,
    connect_args={"check_same_thread": False},
    future=True
)
# Enforce foreign keys in SQLite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()
def get_connection():
    return engine.connect()
def reflect_table(table_name: str) -> Table:
    """
    Reflect and return a Table object for the given table_name.
    Raises if not existing.
    """
    meta = MetaData()
    try:
        meta.reflect(bind=engine, only=[table_name])
    except Exception:
        meta = MetaData()
        meta.reflect(bind=engine)
    if table_name in meta.tables:
        return meta.tables[table_name]
    raise RuntimeError(f"Table '{table_name}' does not exist in database.")
def table_exists(table_name: str) -> bool:
    meta = MetaData()
    meta.reflect(bind=engine)
    return table_name in meta.tables
def get_table_columns(table_name: str) -> List[Dict]:
    """
    Return list of column info dicts as in PRAGMA table_info
    """
    with engine.connect() as conn:
        res = conn.execute(text(f"PRAGMA table_info('{table_name}')"))
        cols = [dict(row._mapping) for row in res]
        return cols
def ensure_migrations_table():
    """
    Create the migrations tracking table if not exists.
    """
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                step INTEGER NOT NULL UNIQUE,
                name TEXT NOT NULL,
                applied_at TEXT NOT NULL
            )
        """))
def get_applied_steps() -> List[int]:
    ensure_migrations_table()
    with engine.connect() as conn:
        res = conn.execute(text("SELECT step FROM migrations ORDER BY step"))
        return [row[0] for row in res]
def record_migration(step: int, name: str):
    ensure_migrations_table()
    ts = datetime.datetime.utcnow().isoformat()
    with engine.begin() as conn:
        conn.execute(
            text("INSERT OR IGNORE INTO migrations (step, name, applied_at) VALUES (:step, :name, :applied_at)"),
            {"step": step, "name": name, "applied_at": ts}
        )