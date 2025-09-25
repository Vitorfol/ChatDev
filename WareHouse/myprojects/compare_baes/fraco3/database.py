'''
SQLAlchemy database setup: engine, session factory, and declarative base.
'''
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
SQLALCHEMY_DATABASE_URL = "sqlite:///./school.db"
# For SQLite, check_same_thread should be False when using multiple threads (e.g. FastAPI uvicorn)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()