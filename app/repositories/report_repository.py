
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.vehicle_report import VehicleReport
from app.schemas.vehicle_report import VehicleReportCreate


def get_by_id(
    db: Session,
    report_id: UUID,
) -> VehicleReport | None:
    return db.get(VehicleReport, report_id)


def get_pending_by_listing_url(
    db: Session,
    listing_url: str,
) -> VehicleReport | None:
    statement = select(VehicleReport).where(
        VehicleReport.listing_url == listing_url,
        VehicleReport.status == "pending",
    )

    return db.scalars(statement).first()


def create(
    db: Session,
    report_data: VehicleReportCreate,
) -> VehicleReport:
    report = VehicleReport(**report_data.model_dump())

    db.add(report)
    db.flush()
    db.refresh(report)

    return report
