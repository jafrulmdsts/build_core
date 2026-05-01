"""Employee Pydantic schemas (request/response)."""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field


class EmployeeType(str, Enum):
    """Allowed employee type values."""

    FIELD = "field"
    OFFICE = "office"


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------


class EmployeeCreate(BaseModel):
    """Payload for creating a new employee."""

    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field("", max_length=100)
    phone: str = Field("", max_length=20)
    email: str = Field("", max_length=255)
    designation: str = Field("", max_length=100)
    employee_type: str = Field("field", max_length=30)
    department: str = Field("", max_length=100)
    salary: Decimal | None = None
    currency_code: str = Field("BDT", max_length=3)
    joining_date: date | None = None
    nid_number: str = Field("", max_length=50)
    address: str | None = None
    emergency_contact: str = Field("", max_length=200)
    bank_account: str = Field("", max_length=100)


class EmployeeUpdate(BaseModel):
    """Payload for updating an existing employee (all fields optional)."""

    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, max_length=100)
    phone: str | None = Field(None, max_length=20)
    email: str | None = Field(None, max_length=255)
    designation: str | None = Field(None, max_length=100)
    employee_type: str | None = Field(None, max_length=30)
    department: str | None = Field(None, max_length=100)
    salary: Decimal | None = None
    currency_code: str | None = Field(None, max_length=3)
    joining_date: date | None = None
    nid_number: str | None = Field(None, max_length=50)
    address: str | None = None
    emergency_contact: str | None = Field(None, max_length=200)
    bank_account: str | None = Field(None, max_length=100)
    is_active: bool | None = None


# ---------------------------------------------------------------------------
# Response schema
# ---------------------------------------------------------------------------


class EmployeeResponse(BaseModel):
    """Employee data returned by the API."""

    id: str
    organization_id: str
    employee_code: str
    first_name: str
    last_name: str | None = None
    phone: str | None = None
    email: str | None = None
    designation: str | None = None
    employee_type: str | None = None
    department: str | None = None
    salary: Decimal | None = None
    currency_code: str = "BDT"
    joining_date: date | None = None
    nid_number: str | None = None
    address: str | None = None
    emergency_contact: str | None = None
    bank_account: str | None = None
    is_active: bool = True
    created_by: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
