"""Location hierarchy models — Country, Division, District, Upazila, PostOffice.

All relations use soft String(36) IDs (no foreign keys).
All business tables inherit from BaseModel (includes soft-delete via deleted_at).
"""

from sqlalchemy import Boolean, Column, String

from app.models.base import BaseModel


class Country(BaseModel):
    """Top-level country entity (e.g. Bangladesh)."""

    __tablename__ = "countries"

    name = Column(String(100), nullable=False)
    code = Column(String(10), nullable=False)  # ISO country code like "BD"
    is_active = Column(Boolean, default=True)


class Division(BaseModel):
    """Administrative division / province (e.g. Dhaka Division)."""

    __tablename__ = "divisions"

    country_id = Column(String(36), nullable=False)  # soft ref to countries
    name = Column(String(100), nullable=False)
    name_bn = Column(String(100), nullable=False)  # Bangla name
    code = Column(String(20), nullable=False)
    is_active = Column(Boolean, default=True)


class District(BaseModel):
    """District within a division (e.g. Dhaka District)."""

    __tablename__ = "districts"

    division_id = Column(String(36), nullable=False)  # soft ref to divisions
    name = Column(String(100), nullable=False)
    name_bn = Column(String(100), nullable=False)
    code = Column(String(20), nullable=False)
    is_active = Column(Boolean, default=True)


class Upazila(BaseModel):
    """Sub-district / upazila within a district (e.g. Dhanmondi)."""

    __tablename__ = "upazilas"

    district_id = Column(String(36), nullable=False)  # soft ref to districts
    name = Column(String(100), nullable=False)
    name_bn = Column(String(100), nullable=False)
    code = Column(String(20), nullable=False)
    is_active = Column(Boolean, default=True)


class PostOffice(BaseModel):
    """Post office within an upazila (e.g. Dhanmondi PO, 1205)."""

    __tablename__ = "post_offices"

    upazila_id = Column(String(36), nullable=False)  # soft ref to upazilas
    name = Column(String(100), nullable=False)
    name_bn = Column(String(100), nullable=False)
    code = Column(String(20), nullable=False)  # Post code
    is_active = Column(Boolean, default=True)
