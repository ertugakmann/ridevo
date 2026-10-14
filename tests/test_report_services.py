from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.services import report_services
from app.services.report_services import (
    ReportAlreadyProcessingError,
    ReportNotFoundError,
)
from app.schemas.vehicle_report import VehicleReportCreate

LISTING_URL = "https://example.com/listings/123"


@pytest.fixture
def repository(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    mock_repository = MagicMock()
    mock_repository.get_pending_by_listing_url.return_value = None
    monkeypatch.setattr(report_services, "report_repository", mock_repository)
    return mock_repository


@pytest.fixture
def db() -> MagicMock:
    return MagicMock()


def report_data(listing_url: str | None = LISTING_URL) -> VehicleReportCreate:
    return VehicleReportCreate(listing_url=listing_url, make="Toyota", model="Corolla")


def test_get_report_returns_report(repository: MagicMock, db: MagicMock) -> None:
    report_id = uuid4()

    result = report_services.get_report(db, report_id)

    assert result is repository.get_by_id.return_value
    repository.get_by_id.assert_called_once_with(db, report_id)


def test_get_report_raises_when_missing(repository: MagicMock, db: MagicMock) -> None:
    repository.get_by_id.return_value = None

    with pytest.raises(ReportNotFoundError):
        report_services.get_report(db, uuid4())


def test_create_report_commits_and_returns_report(
    repository: MagicMock,
    db: MagicMock,
) -> None:
    data = report_data()

    result = report_services.create_report(db, data)

    assert result is repository.create.return_value
    repository.create.assert_called_once_with(db, data)
    db.commit.assert_called_once()
    db.rollback.assert_not_called()


def test_create_report_raises_when_listing_is_pending(
    repository: MagicMock,
    db: MagicMock,
) -> None:
    repository.get_pending_by_listing_url.return_value = MagicMock()

    with pytest.raises(ReportAlreadyProcessingError):
        report_services.create_report(db, report_data())

    repository.get_pending_by_listing_url.assert_called_once_with(db, LISTING_URL)
    repository.create.assert_not_called()
    db.commit.assert_not_called()


def test_create_report_skips_pending_lookup_without_listing_url(
    repository: MagicMock,
    db: MagicMock,
) -> None:
    report_services.create_report(db, report_data(listing_url=None))

    repository.get_pending_by_listing_url.assert_not_called()
    repository.create.assert_called_once()


def test_create_report_rolls_back_when_persistence_fails(
    repository: MagicMock,
    db: MagicMock,
) -> None:
    repository.create.side_effect = SQLAlchemyError("insert failed")

    with pytest.raises(SQLAlchemyError):
        report_services.create_report(db, report_data())

    db.rollback.assert_called_once()
    db.commit.assert_not_called()


def test_create_report_rolls_back_when_commit_fails(
    repository: MagicMock,
    db: MagicMock,
) -> None:
    db.commit.side_effect = SQLAlchemyError("commit failed")

    with pytest.raises(SQLAlchemyError):
        report_services.create_report(db, report_data())

    db.rollback.assert_called_once()
