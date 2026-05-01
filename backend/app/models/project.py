"""Project SQLAlchemy model.

Stores construction project records scoped to an organization.
All foreign references use soft String(36) IDs validated at the service layer.
"""

from sqlalchemy import Column, String, DateTime, Boolean, Text, Numeric, Integer, Date, func, UniqueConstraint

from app.models.base import BaseModel


class Project(BaseModel):
    __tablename__ = "projects"
    __table_args__ = (
        UniqueConstraint("organization_id", "code", name="uq_project_org_code"),
    )

    organization_id = Column(String(36), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    code = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    country_id = Column(String(36), nullable=True)
    division_id = Column(String(36), nullable=True)
    district_id = Column(String(36), nullable=True)
    upazila_id = Column(String(36), nullable=True)
    post_office_id = Column(String(36), nullable=True)
    village = Column(String(200), nullable=True)
    full_address = Column(Text, nullable=True)
    latitude = Column(Numeric(10, 8), nullable=True)
    longitude = Column(Numeric(11, 8), nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    estimated_budget = Column(Numeric(15, 2), nullable=True)
    currency_code = Column(String(3), default="BDT")
    status = Column(String(30), default="planned")
    project_type = Column(String(50), nullable=True)
    manager_id = Column(String(36), nullable=True)
    client_name = Column(String(200), nullable=True)
    client_phone = Column(String(20), nullable=True)
    client_email = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    created_by = Column(String(36), nullable=True)
    updated_by = Column(String(36), nullable=True)
