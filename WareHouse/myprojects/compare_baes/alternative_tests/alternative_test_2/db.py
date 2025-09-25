'''
Database setup using SQLAlchemy. Provides engine, Base, and a get_db dependency.
'''
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from typing import Generator
DATABASE_URL = "sqlite:///./academic.db"
# For SQLite, disable check_same_thread to allow sessions from different threads (FastAPI workers)
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a SQLAlchemy session and closes it afterwards.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()