'''
Simple in-process migration runner:
- Ensures a migrations table exists.
- Applies .sql files inside migrations/ directory in alphabetical order.
- Records applied migrations to avoid re-applying.
This satisfies the requirement to provide migration scripts and apply them at runtime without restarting.
This migration runner is hardened to sanitize accidental Python triple-quoted blocks and provide improved diagnostics.
'''
'''
Simple in-process migration runner:
- Ensures a migrations table exists.
- Applies .sql files inside migrations/ directory in alphabetical order.
- Records applied migrations to avoid re-applying.
This satisfies the requirement to provide migration scripts and apply them at runtime without restarting.
This migration runner is hardened to sanitize accidental Python triple-quoted blocks and provide improved diagnostics.
'''
import os
import sqlite3
import re
from datetime import datetime
MIGRATIONS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    applied_at TEXT NOT NULL
);
"""
def _ensure_migrations_table(conn: sqlite3.Connection):
    conn.execute(MIGRATIONS_TABLE_SQL)
    conn.commit()
def _get_applied_migrations(conn: sqlite3.Connection):
    cur = conn.execute("SELECT name FROM migrations")
    rows = cur.fetchall()
    return {r[0] for r in rows}
def _sanitize_sql_content(sql: str) -> str:
    """
    Remove accidental Python-style triple-quoted blocks and leading/trailing whitespace.
    Also handles both '''...''' and \"\"\"...\"\"\" forms. Returns sanitized SQL string.
    """
    if not sql:
        return ""
    # Remove any leading/trailing Python triple-quoted blocks
    # Use DOTALL to allow newlines inside quotes
    sanitized = re.sub(r"(?s)^(?:'''|\"\"\").*?(?:'''|\"\"\")", "", sql).strip()
    # Additionally, remove any trailing triple-quoted blocks if present
    sanitized = re.sub(r"(?s)(?:'''|\"\"\").*?(?:'''|\"\"\")$", "", sanitized).strip()
    return sanitized
def apply_migrations(db_path: str, migrations_dir: str):
    """
    Apply SQL migration files from migrations_dir to the SQLite database at db_path.
    Uses a migrations table to track applied migrations and avoid reapplying.
    Provides better diagnostics and sanitization to tolerate accidental non-SQL text.
    Raises RuntimeError on failure with context about the migration file.
    """
    os.makedirs(migrations_dir, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        _ensure_migrations_table(conn)
        applied = _get_applied_migrations(conn)
        # List .sql files sorted
        files = sorted([f for f in os.listdir(migrations_dir) if f.endswith(".sql")])
        for fname in files:
            if fname in applied:
                continue
            full = os.path.join(migrations_dir, fname)
            with open(full, "r", encoding="utf-8") as fh:
                raw_sql = fh.read()
            # Sanitize SQL content to remove accidental Python triple-quoted blocks
            sql = _sanitize_sql_content(raw_sql)
            if not sql:
                # If sanitized SQL is empty, skip executing but mark migration applied to avoid reprocessing.
                print(f"Skipping migration {fname}: no SQL after sanitization.")
                conn.execute(
                    "INSERT INTO migrations (name, applied_at) VALUES (?, ?)",
                    (fname, datetime.utcnow().isoformat())
                )
                conn.commit()
                continue
            print(f"Applying migration: {fname}")
            try:
                conn.executescript(sql)
                conn.execute(
                    "INSERT INTO migrations (name, applied_at) VALUES (?, ?)",
                    (fname, datetime.utcnow().isoformat())
                )
                conn.commit()
            except Exception as exc:
                conn.rollback()
                # Provide clear, actionable error including filename and snippet of SQL
                snippet = sql[:400].replace("\n", "\\n")
                err_msg = f"Failed to apply migration '{fname}': {exc}. SQL snippet (truncated): {snippet!s}"
                print(err_msg)
                raise RuntimeError(err_msg) from exc
    finally:
        conn.close()