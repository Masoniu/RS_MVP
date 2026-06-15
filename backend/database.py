"""
File: database.py

Database connection setup using SQLAlchemy.

Responsibilities:
- Reading the connection string from .env (DATABASE_URL)
- Creating the engine and session factory (SessionLocal)
- Providing the base class for ORM models (Base)
- FastAPI dependency get_db() for injecting a session into route handlers
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# PostgreSQL connection URL, e.g.:
# postgresql://user:password@localhost:5432/routesplitter
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# SQLAlchemy engine — single instance per process
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Session factory:
#   autocommit=False — transactions must be committed/rolled back explicitly
#   autoflush=False  — changes are not flushed to the DB automatically before queries
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for all ORM models in the project."""
    pass


def get_db():
    """
    Generator dependency for FastAPI to obtain a database session.

    Opens a new session for the duration of a single HTTP request
    and guarantees it is closed after the response (even on exceptions).

    Yields:
        Session: an active SQLAlchemy session bound to the current request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()