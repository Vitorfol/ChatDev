'''
Simple migrations runner. It records applied migrations in a "migrations" table and applies
any new SQL files in the migrations/ directory in lexical order.
'''
import os
import sqlite3
from typing import List
MIGRATIONS_DIR = os.path.join(os.path.dirname(__file__), "migrations")
DATABASE_FILE = os.path.join(os.path.dirname(__file__), "academic.db")
def _ensure_migrations_table(conn: sqlite3.Connection):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL UNIQUE,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    conn.commit()
def _get_applied_migrations(conn: sqlite3.Connection) -> List[str]:
    cur = conn.execute("SELECT filename FROM migrations ORDER BY id;")
    return [row[0] for row in cur.fetchall()]
def _list_migration_files() -> List[str]:
    files = []
    if not os.path.isdir(MIGRATIONS_DIR):
        return files
    for fn in sorted(os.listdir(MIGRATIONS_DIR)):
        if fn.endswith(".sql"):
            files.append(fn)
    return files
def run_migrations():
    """
    Connects to the SQLite database at DATABASE_FILE (created if missing), ensures the migrations
    table, and applies any new SQL migration files in migrations/ directory.
    """
    # Ensure the database file exists by connecting.
    conn = sqlite3.connect(DATABASE_FILE)
    try:
        _ensure_migrations_table(conn)
        applied = set(_get_applied_migrations(conn))
        files = _list_migration_files()
        for fn in files:
            if fn in applied:
                continue
            path = os.path.join(MIGRATIONS_DIR, fn)
            with open(path, "r", encoding="utf-8") as f:
                sql = f.read()
            if not sql.strip():
                continue
            print(f"Applying migration: {fn}")
            try:
                conn.executescript(sql)
                conn.execute("INSERT INTO migrations (filename) VALUES (?);", (fn,))
                conn.commit()
            except Exception as exc:
                conn.rollback()
                print(f"Failed to apply migration {fn}: {exc}")
                raise
    finally:
        conn.close()