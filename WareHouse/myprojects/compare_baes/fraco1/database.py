'''
Database utilities: SQLAlchemy engine, session local, and dependency for FastAPI.
Initializes the SQLite database and provides get_db dependency for request-scoped sessions.
This module ensures foreign key enforcement for SQLite and provides a simple Database
manager used by the FastAPI app.
'''
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError
from models import Base
# SQLite file URL
DATABASE_URL = "sqlite:///./app.db"
# Create engine with the required check_same_thread flag for SQLite + threading
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
# Ensure SQLite enforces foreign key constraints on each new connection
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    try:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    except Exception:
        # If we cannot set the pragma, ignore silently (best-effort)
        pass
# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
class Database:
    '''
    Database manager class that encapsulates engine and session factory.
    Provides methods to initialize the database and to yield request-scoped sessions.
    '''
    def __init__(self, engine: Engine, session_factory: sessionmaker):
        self.engine = engine
        self.SessionLocal = session_factory
    def init_db(self) -> None:
        """
        Create database tables based on SQLAlchemy models (Base.metadata).
        Raises RuntimeError if initialization fails.
        """
        try:
            Base.metadata.create_all(bind=self.engine)
        except OperationalError as e:
            raise RuntimeError("Failed to initialize database: " + str(e))
    def get_db(self):
        """
        Dependency generator that yields a SQLAlchemy session and ensures it's closed.
        Use in FastAPI endpoints as: Depends(database.get_db)
        """
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
# Singleton-like module-level instance for convenience
_db = Database(engine, SessionLocal)
def init_db() -> None:
    """
    Module-level helper to initialize the database tables.
    """
    _db.init_db()
def get_db():
    """
    Module-level dependency generator for FastAPI endpoints.
    Example:
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            ...
    This function yields from the Database.get_db generator so it works correctly
    as a FastAPI dependency (a generator-based dependency).
    """
    # Yield from the instance method generator so FastAPI receives a generator.
    yield from _db.get_db()