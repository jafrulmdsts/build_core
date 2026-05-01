"""Contractor Pydantic schemas (request/response)."""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field


class ContractStatus(str, Enum):
    """Allowed contract status values."""

    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    TERMINATED = "terminated"


class PaymentStatus(str, Enum):
    """Allowed payment status values."""

    PENDING = "pending"
    APPROVED = "approved"
    PAID = "paid"
    PARTIALLY_PAID = "partially_paid"


# ---------------------------------------------------------------------------
# Contractor schemas
# ---------------------------------------------------------------------------


class ContractorCreate(BaseModel):
    """Payload for creating a new contractor."""

    name: str = Field(..., min_length=1, max_length=200)
    phone: str = Field("", max_length=20)
    email: str = Field("", max_length=255)
    address: str | None = None
    nid_number: str = Field("", max_length=50)
    trade_license: str = Field("", max_length=100)
    bank_account: str = Field("", max_length=100)
    notes: str | None = None


class ContractorUpdate(BaseModel):
    """Payload for updating an existing contractor (all fields optional)."""

    name: str | None = Field(None, min_length=1, max_length=200)
    phone: str | None = Field(None, max_length=20)
    email: str | None = Field(None, max_length=255)
    address: str | None = None
    nid_number: str | None = Field(None, max_length=50)
    trade_license: str | None = Field(None, max_length=100)
    bank_account: str | None = Field(None, max_length=100)
    notes: str | None = None
    is_active: bool | None = None


class ContractorResponse(BaseModel):
    """Contractor data returned by the API."""

    id: str
    organization_id: str
    contractor_code: str
    name: str
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    nid_number: str | None = None
    trade_license: str | None = None
    bank_account: str | None = None
    notes: str | None = None
    is_active: bool = True
    created_by: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# ContractorContract schemas
# ---------------------------------------------------------------------------


class ContractCreate(BaseModel):
    """Payload for creating a new contractor contract."""

    project_id: str = Field(..., min_length=1, max_length=36)
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    work_scope: str | None = None
    total_amount: Decimal | None = None
    currency_code: str = Field("BDT", max_length=3)
    start_date: date | None = None
    end_date: date | None = None
    payment_terms: str | None = None
    status: str = Field("draft", max_length=30)
    notes: str | None = None


class ContractUpdate(BaseModel):
    """Payload for updating an existing contractor contract (all fields optional)."""

    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    work_scope: str | None = None
    total_amount: Decimal | None = None
    currency_code: str | None = Field(None, max_length=3)
    start_date: date | None = None
    end_date: date | None = None
    payment_terms: str | None = None
    status: str | None = Field(None, max_length=30)
    notes: str | None = None


class ContractResponse(BaseModel):
    """Contractor contract data returned by the API."""

    id: str
    organization_id: str
    contractor_id: str
    project_id: str
    contract_code: str
    title: str
    description: str | None = None
    work_scope: str | None = None
    total_amount: Decimal | None = None
    currency_code: str = "BDT"
    start_date: date | None = None
    end_date: date | None = None
    payment_terms: str | None = None
    status: str = "draft"
    notes: str | None = None
    created_by: str | None = None
    updated_by: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# ContractorPayment schemas
# ---------------------------------------------------------------------------


class PaymentCreate(BaseModel):
    """Payload for creating a new contractor payment."""

    amount: Decimal = Field(..., gt=0)
    currency_code: str = Field("BDT", max_length=3)
    payment_date: date | None = None
    due_date: date | None = None
    status: str = Field("pending", max_length=30)
    payment_method: str | None = Field(None, max_length=50)
    reference_number: str | None = Field(None, max_length=100)
    notes: str | None = None


class PaymentUpdate(BaseModel):
    """Payload for updating an existing contractor payment (all fields optional)."""

    amount: Decimal | None = Field(None, gt=0)
    currency_code: str | None = Field(None, max_length=3)
    payment_date: date | None = None
    due_date: date | None = None
    status: str | None = Field(None, max_length=30)
    approved_by: str | None = None
    payment_method: str | None = Field(None, max_length=50)
    reference_number: str | None = Field(None, max_length=100)
    notes: str | None = None


class PaymentResponse(BaseModel):
    """Contractor payment data returned by the API."""

    id: str
    organization_id: str
    contract_id: str
    payment_no: int
    amount: Decimal
    currency_code: str = "BDT"
    payment_date: date | None = None
    due_date: date | None = None
    status: str = "pending"
    approved_by: str | None = None
    payment_method: str | None = None
    reference_number: str | None = None
    notes: str | None = None
    created_by: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
