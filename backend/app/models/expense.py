"""
Project Expense Model.

Tracks individual project expenses with categories, approval workflow,
and multi-currency support. Soft-references projects via project_id
(validated at service layer, no foreign key).
"""

from sqlalchemy import Column, String, Text, Numeric, Date
from app.models.base import BaseModel


class ProjectExpense(BaseModel):
    __tablename__ = "project_expenses"

    organization_id = Column(String(36), nullable=False)
    project_id = Column(String(36), nullable=False)  # soft ref to projects
    expense_code = Column(String(50), nullable=False)  # e.g., EXP-001
    category = Column(String(50), nullable=True)  # material, labor, transport, equipment, misc
    description = Column(Text, nullable=True)
    amount = Column(Numeric(15, 2), nullable=False)
    currency_code = Column(String(3), default="BDT")
    expense_date = Column(Date, nullable=True)
    recorded_by = Column(String(36), nullable=True)  # soft ref to users/employees
    approved_by = Column(String(36), nullable=True)
    approval_status = Column(String(30), default="pending")  # pending, approved, rejected
    payment_method = Column(String(50), nullable=True)  # cash, bank_transfer
    receipt_url = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)
