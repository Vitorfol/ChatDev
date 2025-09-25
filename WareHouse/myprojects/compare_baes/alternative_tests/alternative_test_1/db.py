'''
Database utilities: SQLAlchemy engine, SessionLocal, and dependency for FastAPI endpoints.
Enables SQLite foreign keys pragma on connect.
'''
'''
Database utilities: SQLAlchemy engine, SessionLocal, and dependency for FastAPI endpoints.
Enables SQLite foreign keys pragma on connect.
'''
import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, scoped_session
from typing import Generator
_engine = None
_SessionLocal = None
def get_engine(db_path: str):
    """
    Create and return a SQLAlchemy engine for the given SQLite database path.
    Ensures PRAGMA foreign_keys=ON for connections.
    """
    global _engine
    if _engine is None:
        db_url = f"sqlite:///{db_path}"
        _engine = create_engine(db_url, connect_args={"check_same_thread": False})
        # Ensure foreign keys are enabled
        @event.listens_for(_engine, "connect")
        def _set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON;")
            cursor.close()
    return _engine
def init_db_session(engine):
    """
    Initialize the global sessionmaker using the provided engine.
    """
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
def get_db() -> Generator:
    """
    FastAPI dependency to provide DB sessions.
    Commits after successful request, rolls back on exception.
    """
    global _SessionLocal
    if _SessionLocal is None:
        raise RuntimeError("SessionLocal not initialized. Call init_db_session(engine) first.")
    db = _SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()