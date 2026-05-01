"""Project Pydantic schemas for request validation and API responses.

Python enums validate status and project_type values — no DB ENUMs.
"""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class ProjectStatus(str, Enum):
    PLANNED = "planned"
    ONGOING = "ongoing"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProjectType(str, Enum):
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    country_id: str | None = None
    division_id: str | None = None
    district_id: str | None = None
    upazila_id: str | None = None
    post_office_id: str | None = None
    village: str | None = Field(None, max_length=200)
    full_address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    start_date: date | None = None
    end_date: date | None = None
    estimated_budget: Decimal | None = None
    currency_code: str = Field("BDT", max_length=3)
    status: str = Field("planned", max_length=30)
    project_type: str | None = Field(None, max_length=50)
    manager_id: str | None = None
    client_name: str | None = Field(None, max_length=200)
    client_phone: str | None = Field(None, max_length=20)
    client_email: str | None = Field(None, max_length=255)
    notes: str | None = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        valid = {e.value for e in ProjectStatus}
        if v not in valid:
            raise ValueError(
                f"Invalid status '{v}'. Must be one of: {', '.join(sorted(valid))}"
            )
        return v

    @field_validator("project_type")
    @classmethod
    def validate_project_type(cls, v: str | None) -> str | None:
        if v is None:
            return v
        valid = {e.value for e in ProjectType}
        if v not in valid:
            raise ValueError(
                f"Invalid project_type '{v}'. Must be one of: {', '.join(sorted(valid))}"
            )
        return v


class ProjectUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    country_id: str | None = None
    division_id: str | None = None
    district_id: str | None = None
    upazila_id: str | None = None
    post_office_id: str | None = None
    village: str | None = Field(None, max_length=200)
    full_address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    start_date: date | None = None
    end_date: date | None = None
    estimated_budget: Decimal | None = None
    currency_code: str | None = Field(None, max_length=3)
    status: str | None = Field(None, max_length=30)
    project_type: str | None = Field(None, max_length=50)
    manager_id: str | None = None
    client_name: str | None = Field(None, max_length=200)
    client_phone: str | None = Field(None, max_length=20)
    client_email: str | None = Field(None, max_length=255)
    notes: str | None = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str | None) -> str | None:
        if v is None:
            return v
        valid = {e.value for e in ProjectStatus}
        if v not in valid:
            raise ValueError(
                f"Invalid status '{v}'. Must be one of: {', '.join(sorted(valid))}"
            )
        return v

    @field_validator("project_type")
    @classmethod
    def validate_project_type(cls, v: str | None) -> str | None:
        if v is None:
            return v
        valid = {e.value for e in ProjectType}
        if v not in valid:
            raise ValueError(
                f"Invalid project_type '{v}'. Must be one of: {', '.join(sorted(valid))}"
            )
        return v


class ProjectResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    code: str
    description: str | None = None
    country_id: str | None = None
    division_id: str | None = None
    district_id: str | None = None
    upazila_id: str | None = None
    post_office_id: str | None = None
    village: str | None = None
    full_address: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    start_date: date | None = None
    end_date: date | None = None
    estimated_budget: Decimal | None = None
    currency_code: str = "BDT"
    status: str = "planned"
    project_type: str | None = None
    manager_id: str | None = None
    client_name: str | None = None
    client_phone: str | None = None
    client_email: str | None = None
    notes: str | None = None
    created_by: str | None = None
    updated_by: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
