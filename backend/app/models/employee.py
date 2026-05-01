"""Employee model — construction workforce entity."""

from sqlalchemy import Column, String, DateTime, Boolean, Text, Numeric, Integer, Date

from app.models.base import BaseModel


class Employee(BaseModel):
    """Represents a full-time or field employee of an organization."""

    __tablename__ = "employees"

    organization_id = Column(String(36), nullable=False)
    employee_code = Column(String(50), nullable=False)  # e.g., EMP-001
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    designation = Column(String(100), nullable=True)
    employee_type = Column(String(30), nullable=True)  # field, office
    department = Column(String(100), nullable=True)
    salary = Column(Numeric(12, 2), nullable=True)
    currency_code = Column(String(3), default="BDT")
    joining_date = Column(Date, nullable=True)
    nid_number = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    emergency_contact = Column(String(200), nullable=True)
    bank_account = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_by = Column(String(36), nullable=True)
