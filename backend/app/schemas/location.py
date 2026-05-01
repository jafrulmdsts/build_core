"""Location Pydantic schemas (response).

All fields use camelCase for API; snake_case mapping handled by Pydantic.
"""

from datetime import datetime

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Response schemas for each entity
# ---------------------------------------------------------------------------


class CountryResponse(BaseModel):
    """Country data returned by the API."""

    id: str
    name: str
    code: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DivisionResponse(BaseModel):
    """Division data returned by the API."""

    id: str
    country_id: str
    name: str
    name_bn: str
    code: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DistrictResponse(BaseModel):
    """District data returned by the API."""

    id: str
    division_id: str
    name: str
    name_bn: str
    code: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UpazilaResponse(BaseModel):
    """Upazila data returned by the API."""

    id: str
    district_id: str
    name: str
    name_bn: str
    code: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PostOfficeResponse(BaseModel):
    """Post office data returned by the API."""

    id: str
    upazila_id: str
    name: str
    name_bn: str
    code: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Composite response schemas
# ---------------------------------------------------------------------------


class LocationChainResponse(BaseModel):
    """Complete location chain from country to post office.

    Used by projects and other entities to resolve the full
    administrative hierarchy from any point in the chain.
    """

    country: CountryResponse | None = None
    division: DivisionResponse | None = None
    district: DistrictResponse | None = None
    upazila: UpazilaResponse | None = None
    post_office: PostOfficeResponse | None = None
