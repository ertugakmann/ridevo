from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine
from sqlalchemy.exc import OperationalError

from app import main
from app.main import app

client = TestClient(app)


def test_ready_reports_connected_database(
    monkeypatch: pytest.MonkeyPatch,
    engine: Engine,
) -> None:
    monkeypatch.setattr(main, "engine", engine)

    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "database": "connected",
    }


def test_ready_returns_503_when_database_connection_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    failing_engine = MagicMock()
    failing_engine.connect.side_effect = OperationalError(
        "SELECT 1", {}, Exception("connection refused")
    )
    monkeypatch.setattr(main, "engine", failing_engine)

    response = client.get("/ready")

    assert response.status_code == 503
    assert response.json() == {"detail": "Database connection failed"}
