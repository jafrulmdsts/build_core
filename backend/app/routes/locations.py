"""
BuildCore Location Hierarchy Routes.

Endpoints for browsing the administrative location tree
(Country → Division → District → Upazila → Post Office).
Reference data endpoints — no authentication required for reads.
"""

from fastapi import APIRouter, Depends

from app.core.dependencies import get_db_session
from app.core.responses import success_response
from app.services.location.service import (
    list_countries,
    list_districts,
    list_divisions,
    list_post_offices,
    list_upazilas,
)

router = APIRouter(prefix="/locations", tags=["Locations"])


@router.get("/countries")
async def get_countries(
    db=Depends(get_db_session),
):
    """List all active countries.

    Returns the full list of countries ordered by name.
    No authentication required — this is reference data.
    """
    countries = await list_countries(db)
    return success_response(data=countries, message="Countries retrieved")


@router.get("/countries/{country_id}/divisions")
async def get_divisions_by_country(
    country_id: str,
    db=Depends(get_db_session),
):
    """List active divisions for a given country.

    Args:
        country_id: UUID of the parent country.
    """
    divisions = await list_divisions(db, country_id)
    return success_response(data=divisions, message="Divisions retrieved")


@router.get("/divisions/{division_id}/districts")
async def get_districts_by_division(
    division_id: str,
    db=Depends(get_db_session),
):
    """List active districts for a given division.

    Args:
        division_id: UUID of the parent division.
    """
    districts = await list_districts(db, division_id)
    return success_response(data=districts, message="Districts retrieved")


@router.get("/districts/{district_id}/upazilas")
async def get_upazilas_by_district(
    district_id: str,
    db=Depends(get_db_session),
):
    """List active upazilas for a given district.

    Args:
        district_id: UUID of the parent district.
    """
    upazilas = await list_upazilas(db, district_id)
    return success_response(data=upazilas, message="Upazilas retrieved")


@router.get("/upazilas/{upazila_id}/post-offices")
async def get_post_offices_by_upazila(
    upazila_id: str,
    db=Depends(get_db_session),
):
    """List active post offices for a given upazila.

    Args:
        upazila_id: UUID of the parent upazila.
    """
    post_offices = await list_post_offices(db, upazila_id)
    return success_response(data=post_offices, message="Post offices retrieved")
