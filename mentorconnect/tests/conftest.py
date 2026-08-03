"""
tests/conftest.py
--------------------
Shared pytest fixtures: an isolated in-memory SQLite test database (swapped
in for MySQL during tests for speed/isolation) and a FastAPI TestClient
with the DB dependency overridden.

Run with:  pytest -v
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.db.base_class import Base
from app.db.session import get_db
import app.models  # noqa: F401 ensure all models are registered on Base.metadata
from app.models.user import Role
from app.models.enums import RoleName

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def db_session():
    """Provides a fresh in-memory SQLite session per test function."""
    engine = create_engine(
        SQLALCHEMY_TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    # Seed the 3 RBAC roles, since most flows depend on them existing
    for role_name in RoleName:
        session.add(Role(name=role_name, description=role_name.value))
    session.commit()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """FastAPI TestClient with the get_db dependency overridden to use the test DB session."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
