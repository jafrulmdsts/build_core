"""Location service layer — business logic and validation.

Validates parent entity existence before returning children,
and provides full location-chain resolution for projects.
"""

from app.core.exceptions import NotFoundError
from app.models.location import Country, District, Division, PostOffice, Upazila
from app.schemas.location import (
    CountryResponse,
    DistrictResponse,
    DivisionResponse,
    LocationChainResponse,
    PostOfficeResponse,
    UpazilaResponse,
)
from app.services.location import crud


# ---------------------------------------------------------------------------
# List operations (with parent validation)
# ---------------------------------------------------------------------------


async def list_countries(db) -> list[CountryResponse]:
    """List all active countries.

    Args:
        db: Async database session.

    Returns:
        List of CountryResponse schemas.
    """
    countries = await crud.get_countries(db)
    return [CountryResponse.model_validate(c) for c in countries]


async def list_divisions(db, country_id: str) -> list[DivisionResponse]:
    """List active divisions for a country.

    Validates that the country exists before returning divisions.

    Args:
        db: Async database session.
        country_id: UUID string of the parent country.

    Returns:
        List of DivisionResponse schemas.

    Raises:
        NotFoundError: If the country does not exist.
    """
    country = await crud.get_location_entity(db, Country, country_id)
    if country is None:
        raise NotFoundError(
            message="Country not found",
            details={"country_id": country_id},
        )

    divisions = await crud.get_divisions_by_country(db, country_id)
    return [DivisionResponse.model_validate(d) for d in divisions]


async def list_districts(db, division_id: str) -> list[DistrictResponse]:
    """List active districts for a division.

    Validates that the division exists before returning districts.

    Args:
        db: Async database session.
        division_id: UUID string of the parent division.

    Returns:
        List of DistrictResponse schemas.

    Raises:
        NotFoundError: If the division does not exist.
    """
    division = await crud.get_location_entity(db, Division, division_id)
    if division is None:
        raise NotFoundError(
            message="Division not found",
            details={"division_id": division_id},
        )

    districts = await crud.get_districts_by_division(db, division_id)
    return [DistrictResponse.model_validate(d) for d in districts]


async def list_upazilas(db, district_id: str) -> list[UpazilaResponse]:
    """List active upazilas for a district.

    Validates that the district exists before returning upazilas.

    Args:
        db: Async database session.
        district_id: UUID string of the parent district.

    Returns:
        List of UpazilaResponse schemas.

    Raises:
        NotFoundError: If the district does not exist.
    """
    district = await crud.get_location_entity(db, District, district_id)
    if district is None:
        raise NotFoundError(
            message="District not found",
            details={"district_id": district_id},
        )

    upazilas = await crud.get_upazilas_by_district(db, district_id)
    return [UpazilaResponse.model_validate(u) for u in upazilas]


async def list_post_offices(db, upazila_id: str) -> list[PostOfficeResponse]:
    """List active post offices for an upazila.

    Validates that the upazila exists before returning post offices.

    Args:
        db: Async database session.
        upazila_id: UUID string of the parent upazila.

    Returns:
        List of PostOfficeResponse schemas.

    Raises:
        NotFoundError: If the upazila does not exist.
    """
    upazila = await crud.get_location_entity(db, Upazila, upazila_id)
    if upazila is None:
        raise NotFoundError(
            message="Upazila not found",
            details={"upazila_id": upazila_id},
        )

    post_offices = await crud.get_post_offices_by_upazila(db, upazila_id)
    return [PostOfficeResponse.model_validate(p) for p in post_offices]


# ---------------------------------------------------------------------------
# Full location chain resolution
# ---------------------------------------------------------------------------


async def get_full_location_chain(
    db,
    *,
    country_id: str | None = None,
    division_id: str | None = None,
    district_id: str | None = None,
    upazila_id: str | None = None,
    post_office_id: str | None = None,
) -> LocationChainResponse:
    """Resolve the complete location chain from any point in the hierarchy.

    Given any combination of IDs, walks up/down the hierarchy to build
    the full chain: Country -> Division -> District -> Upazila -> PostOffice.

    If a post_office_id is provided, it resolves the full chain from
    post office up to country. If only a district_id is given, it resolves
    up to country and leaves lower levels as None.

    Args:
        db: Async database session.
        country_id: Optional country UUID.
        division_id: Optional division UUID.
        district_id: Optional district UUID.
        upazila_id: Optional upazila UUID.
        post_office_id: Optional post office UUID.

    Returns:
        LocationChainResponse with all resolved levels.

    Raises:
        NotFoundError: If any referenced entity does not exist.
    """
    chain = LocationChainResponse()

    # If the deepest level is provided, start from there and walk up
    if post_office_id:
        po = await crud.get_location_entity(db, PostOffice, post_office_id)
        if po is None:
            raise NotFoundError(
                message="Post office not found",
                details={"post_office_id": post_office_id},
            )
        chain.post_office = PostOfficeResponse.model_validate(po)
        upazila_id = upazila_id or po.upazila_id

    if upazila_id:
        upa = await crud.get_location_entity(db, Upazila, upazila_id)
        if upa is None:
            raise NotFoundError(
                message="Upazila not found",
                details={"upazila_id": upazila_id},
            )
        chain.upazila = UpazilaResponse.model_validate(upa)
        district_id = district_id or upa.district_id

    if district_id:
        dist = await crud.get_location_entity(db, District, district_id)
        if dist is None:
            raise NotFoundError(
                message="District not found",
                details={"district_id": district_id},
            )
        chain.district = DistrictResponse.model_validate(dist)
        division_id = division_id or dist.division_id

    if division_id:
        div = await crud.get_location_entity(db, Division, division_id)
        if div is None:
            raise NotFoundError(
                message="Division not found",
                details={"division_id": division_id},
            )
        chain.division = DivisionResponse.model_validate(div)
        country_id = country_id or div.country_id

    if country_id:
        cntry = await crud.get_location_entity(db, Country, country_id)
        if cntry is None:
            raise NotFoundError(
                message="Country not found",
                details={"country_id": country_id},
            )
        chain.country = CountryResponse.model_validate(cntry)

    # At minimum, some entity must have been resolved
    if chain.country is None:
        raise NotFoundError(
            message="No valid location reference provided",
            details={
                "country_id": country_id,
                "division_id": division_id,
                "district_id": district_id,
                "upazila_id": upazila_id,
                "post_office_id": post_office_id,
            },
        )

    return chain
