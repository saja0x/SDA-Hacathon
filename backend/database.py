"""
Database setup. Everything SQLAlchemy needs to talk to the database
lives in this file: the engine, the session factory, and the Base class
that our ORM models inherit from.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite keeps the whole database in a single file (app.db) next to this
# script. No server to install, which is why it's great for demos.
# For Postgres you'd swap this string for something like:
# "postgresql://user:password@localhost/dbname"
SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"

# The engine is the actual connection to the database.
# check_same_thread=False is a SQLite-only flag: SQLite normally refuses
# to share a connection across threads, but FastAPI handles each request
# in its own thread, so we have to turn that check off.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# A Session is how the ORM tracks objects and writes changes back to the
# database. sessionmaker gives us a factory so each request can create
# its own short-lived session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Every model class (see models.py) inherits from Base. SQLAlchemy uses
# this to keep a registry of all tables so it can create them later.
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that hands a database session to a route, then
    guarantees it gets closed when the request is done -- even if the
    route raises an exception. One session per request is the standard
    pattern.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
