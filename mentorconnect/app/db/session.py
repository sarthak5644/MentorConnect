"""
app/db/session.py
------------------
SQLAlchemy engine and session factory for MySQL.
Provides a `get_db` dependency used by FastAPI routes for request-scoped DB sessions,
and ensures sessions are always closed (no connection leaks).
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings

# The engine manages a pool of connections to MySQL.
# pool_pre_ping=True -> checks connection liveness before using it (avoids "MySQL server has gone away" errors)
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_pre_ping=True,
    echo=False,  # set True only for verbose SQL debugging
)

# Each instance of SessionLocal is a database session bound to the engine above.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    FastAPI dependency that yields a database session per request
    and guarantees it is closed afterwards, even if an exception occurs.
    Usage: def endpoint(db: Session = Depends(get_db)):
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
