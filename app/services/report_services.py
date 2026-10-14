
from uuid import UUID

from sqlalchemy.orm import Session

from app.repositories import report_repository
from app.models.vehicle_report import VehicleReport
from app.schemas.vehicle_report import VehicleReportCreate


class ReportNotFoundError(Exception):
    pass


class ReportAlreadyProcessingError(Exception):
    pass


def get_report(
    db: Session,
    report_id: UUID,
) -> VehicleReport:
    report = report_repository.get_by_id(db, report_id)

    if report is None:
        raise ReportNotFoundError(
            f"Vehicle report with ID {report_id} not found"
        )

    return report



def create_report(
    db: Session,
    report_data: VehicleReportCreate,
) -> VehicleReport:
    if report_data.listing_url is not None:
        existing_report = report_repository.get_pending_by_listing_url(
            db,
            report_data.listing_url,
        )

        if existing_report is not None:
            raise ReportAlreadyProcessingError(
                "A report for this listing is already processing"
            )

    try:
        report = report_repository.create(db, report_data)
        db.commit()
        db.refresh(report)
        return report

    except Exception:
        db.rollback()
        raise
