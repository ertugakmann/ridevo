
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class VehicleReportCreate(BaseModel):
    listing_url: str | None = Field(default=None, max_length=2048)
    make: str = Field(min_length=1, max_length=100)
    model: str = Field(min_length=1, max_length=100)
    year: int | None = Field(default=None, ge=1886, le=2100)
    mileage: int | None = Field(default=None, ge=0)
    price: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)


class VehicleReportResponse(BaseModel):
    id: UUID
    listing_url: str | None
    make: str
    model: str
    year: int | None
    mileage: int | None
    price: Decimal | None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
