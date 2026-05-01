"""Contractor models — vendor and contract management."""

from sqlalchemy import Column, String, DateTime, Boolean, Text, Numeric, Integer, Date

from app.models.base import BaseModel


class Contractor(BaseModel):
    """Represents an external contractor / vendor."""

    __tablename__ = "contractors"

    organization_id = Column(String(36), nullable=False)
    contractor_code = Column(String(50), nullable=False)  # e.g., CTR-001
    name = Column(String(200), nullable=False)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    address = Column(Text, nullable=True)
    nid_number = Column(String(50), nullable=True)
    trade_license = Column(String(100), nullable=True)
    bank_account = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_by = Column(String(36), nullable=True)


class ContractorContract(BaseModel):
    """Represents a contract between an organization and a contractor."""

    __tablename__ = "contractor_contracts"

    organization_id = Column(String(36), nullable=False)
    contractor_id = Column(String(36), nullable=False)  # soft ref
    project_id = Column(String(36), nullable=False)  # soft ref
    contract_code = Column(String(50), nullable=False)  # e.g., CC-001
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    work_scope = Column(Text, nullable=True)
    total_amount = Column(Numeric(15, 2), nullable=True)
    currency_code = Column(String(3), default="BDT")
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    payment_terms = Column(Text, nullable=True)  # JSONB as text
    status = Column(String(30), default="draft")  # draft, active, completed, terminated
    notes = Column(Text, nullable=True)
    created_by = Column(String(36), nullable=True)
    updated_by = Column(String(36), nullable=True)


class ContractorPayment(BaseModel):
    """Represents a payment made against a contractor contract."""

    __tablename__ = "contractor_payments"

    organization_id = Column(String(36), nullable=False)
    contract_id = Column(String(36), nullable=False)  # soft ref
    payment_no = Column(Integer, nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    currency_code = Column(String(3), default="BDT")
    payment_date = Column(Date, nullable=True)
    due_date = Column(Date, nullable=True)
    status = Column(String(30), default="pending")  # pending, approved, paid, partially_paid
    approved_by = Column(String(36), nullable=True)
    payment_method = Column(String(50), nullable=True)  # bank_transfer, cash, cheque
    reference_number = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_by = Column(String(36), nullable=True)
