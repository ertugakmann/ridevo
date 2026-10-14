
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.session import get_db
from app.models.vehicle_report import VehicleReport
from app.schemas.vehicle_report import (
    VehicleReportCreate,
    VehicleReportResponse,
)
from app.services import report_services
from app.services.report_services import (
    ReportAlreadyProcessingError,
    ReportNotFoundError,
)

router = APIRouter(prefix="/reports", tags=["Vehicle Reports"])

@router.get("/{report_id}", response_model=VehicleReportResponse)
def get_report(
    report_id: UUID,
    db: Session = Depends(get_db)
) -> VehicleReport:
    try:
        report = report_services.get_report(db, report_id)
    except ReportNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle report not found",
        ) from exc

    return report

@router.post(
    "",
    response_model=VehicleReportResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_report(
    report_data: VehicleReportCreate,
    db: Session = Depends(get_db),
) -> VehicleReport:
    try:
        report = report_services.create_report(db, report_data)
    except ReportAlreadyProcessingError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A report for this listing is already processing",
        ) from exc

    return report
