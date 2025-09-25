'''
Database setup: SQLAlchemy engine, session factory, and declarative base.
We use SQLite for persistence and a simple sessionmaker. Repositories/services
should import SessionLocal to create DB sessions.
'''
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
DATABASE_URL = "sqlite:///./academic.db"
# echo=False to keep logs minimal; set True for SQL logging
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()