import os

# Point settings at an unreachable placeholder before any app module is
# imported, so no test can ever connect to the development database.
os.environ["DATABASE_URL"] = (
    "postgresql+psycopg://ridevo_test:ridevo_test@127.0.0.1:1/ridevo_test_unused"
)

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import vehicle_report  # noqa: F401  (registers the table)


@pytest.fixture
def engine() -> Iterator[Engine]:
    """A fresh, isolated in-memory SQLite database per test."""
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(test_engine)

    yield test_engine

    test_engine.dispose()


@pytest.fixture
def session_factory(engine: Engine) -> sessionmaker[Session]:
    # Mirrors the options used by app.db.session.SessionLocal.
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@pytest.fixture
def db_session(session_factory: sessionmaker[Session]) -> Iterator[Session]:
    session = session_factory()

    yield session

    session.close()


@pytest.fixture
def client(session_factory: sessionmaker[Session]) -> Iterator[TestClient]:
    def override_get_db() -> Iterator[Session]:
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    # Unhandled server errors become 500 responses so status assertions
    # fail with a clear message instead of a raised exception.
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client

    app.dependency_overrides.clear()
