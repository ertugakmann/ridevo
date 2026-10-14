
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from uuid import UUID

from app.repositories import report_repositories

from app.db.session import get_db
from app.models.vehicle_report import VehicleReport
from app.schemas.vehicle_report import (
    VehicleReportCreate,
    VehicleReportResponse,
)

router = APIRouter(prefix="/reports", tags=["Vehicle Reports"])

@router.get("/{report_id}", response_model=VehicleReportResponse)
def get_report(
    report_id: UUID,
    db: Session = Depends(get_db)
) -> VehicleReport:
    report = report_repositories.get_by_id(db, report_id)

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
    report = report_repositories.create(db, report_data)

    return report
