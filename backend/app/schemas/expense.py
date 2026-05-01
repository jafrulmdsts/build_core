"""
Expense Pydantic Schemas.

Defines request/response schemas for the expense feature.
Uses Python enums for category and approval status validation —
no DB enums per project convention.
"""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field


class ExpenseCategory(str, Enum):
    MATERIAL = "material"
    LABOR = "labor"
    TRANSPORT = "transport"
    EQUIPMENT = "equipment"
    MISC = "misc"


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ExpenseCreate(BaseModel):
    project_id: str
    category: str | None = Field(None, max_length=50)
    description: str | None = None
    amount: Decimal
    currency_code: str = Field("BDT", max_length=3)
    expense_date: date | None = None
    recorded_by: str | None = None
    payment_method: str | None = Field(None, max_length=50)
    receipt_url: str | None = Field(None, max_length=500)
    notes: str | None = None


class ExpenseUpdate(BaseModel):
    category: str | None = Field(None, max_length=50)
    description: str | None = None
    amount: Decimal | None = None
    currency_code: str | None = Field(None, max_length=3)
    expense_date: date | None = None
    payment_method: str | None = Field(None, max_length=50)
    receipt_url: str | None = Field(None, max_length=500)
    notes: str | None = None


class ExpenseApproveRequest(BaseModel):
    status: str = Field("approved", pattern=r"^(approved|rejected)$")
    notes: str | None = None


class ExpenseResponse(BaseModel):
    id: str
    organization_id: str
    project_id: str
    expense_code: str
    category: str | None = None
    description: str | None = None
    amount: Decimal
    currency_code: str = "BDT"
    expense_date: date | None = None
    recorded_by: str | None = None
    approved_by: str | None = None
    approval_status: str = "pending"
    payment_method: str | None = None
    receipt_url: str | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
