from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.vehicle_report import VehicleReport
from app.repositories import report_repository
from app.schemas.vehicle_report import VehicleReportCreate

LISTING_URL = "https://example.com/listings/123"


def add_report(db: Session, **fields: object) -> VehicleReport:
    report = VehicleReport(make="Toyota", model="Corolla", **fields)
    db.add(report)
    db.commit()
    return report


def test_create_persists_report_with_defaults(db_session: Session) -> None:
    data = VehicleReportCreate(listing_url=LISTING_URL, make="Toyota", model="Corolla")

    report = report_repository.create(db_session, data)
    db_session.commit()

    assert report.id is not None
    assert report.status == "pending"
    assert report.created_at is not None
    assert report_repository.get_by_id(db_session, report.id) is report


def test_get_by_id_returns_none_for_missing_report(db_session: Session) -> None:
    assert report_repository.get_by_id(db_session, uuid4()) is None


def test_get_pending_by_listing_url_returns_pending_report(
    db_session: Session,
) -> None:
    pending = add_report(db_session, listing_url=LISTING_URL, status="pending")

    found = report_repository.get_pending_by_listing_url(db_session, LISTING_URL)

    assert found is not None
    assert found.id == pending.id


def test_get_pending_by_listing_url_ignores_non_pending_reports(
    db_session: Session,
) -> None:
    add_report(db_session, listing_url=LISTING_URL, status="completed")
    add_report(db_session, listing_url=LISTING_URL, status="failed")

    assert report_repository.get_pending_by_listing_url(db_session, LISTING_URL) is None


def test_get_pending_by_listing_url_ignores_other_urls(db_session: Session) -> None:
    add_report(db_session, listing_url="https://example.com/listings/456")

    assert report_repository.get_pending_by_listing_url(db_session, LISTING_URL) is None
