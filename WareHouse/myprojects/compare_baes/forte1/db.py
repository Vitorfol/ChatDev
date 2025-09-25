'''
Database helper utilities: file path and connection helper.
We open fresh sqlite3 connections on every operation for simplicity and to allow
ongoing migrations without long-lived ORM metadata conflicts.
'''
import os
import sqlite3
from typing import Iterator
DB_FILENAME = "academic.db"
def get_db_path() -> str:
    """
    Returns the path to the SQLite database file.
    """
    return os.path.abspath(DB_FILENAME)
def connect_db() -> sqlite3.Connection:
    """
    Returns a new sqlite3.Connection with pragmas to improve behavior.
    Uses check_same_thread=False to allow usage from different threads (suitable for this demo).
    """
    conn = sqlite3.connect(get_db_path(), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    # Enable foreign key constraints.
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn