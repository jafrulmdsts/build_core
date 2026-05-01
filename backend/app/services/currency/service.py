"""Currency service layer — business logic and validation.

Handles currency creation, updates, and ensures only one base currency
exists at a time.
"""

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.schemas.currency import CurrencyCreate, CurrencyResponse, CurrencyUpdate
from app.services.currency import crud


async def get_currency(db, currency_id: str) -> CurrencyResponse:
    """Get a single currency by ID.

    Args:
        db: Async database session.
        currency_id: UUID string of the currency.

    Returns:
        CurrencyResponse schema.

    Raises:
        NotFoundError: If the currency does not exist.
    """
    currency = await crud.get_currency_by_id(db, currency_id)
    if currency is None:
        raise NotFoundError(message="Currency not found")
    return CurrencyResponse.model_validate(currency)


async def list_currencies(
    db, page: int = 1, per_page: int = 20
) -> dict:
    """List all active currencies with pagination.

    Args:
        db: Async database session.
        page: 1-based page index.
        per_page: Items per page.

    Returns:
        Dict with items list and pagination metadata.
    """
    items, total = await crud.list_currencies(db, page, per_page)
    total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0
    return {
        "items": [CurrencyResponse.model_validate(c) for c in items],
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages,
    }


async def create_currency(db, data: CurrencyCreate) -> CurrencyResponse:
    """Create a new currency with validation.

    Ensures the ISO code is unique and only one base currency exists.

    Args:
        db: Async database session.
        data: Validated CurrencyCreate payload.

    Returns:
        CurrencyResponse schema for the newly created currency.

    Raises:
        ConflictError: If the currency code already exists.
        ValidationError: If setting a new base currency when one already exists.
    """
    # Check unique code
    existing = await crud.get_currency_by_code(db, data.code)
    if existing is not None:
        raise ConflictError(
            message="Currency code already exists",
            details={"code": data.code},
        )

    # If marking as base currency, ensure no other base exists
    if data.is_base_currency:
        current_base = await crud.get_base_currency(db)
        if current_base is not None:
            raise ValidationError(
                message="A base currency already exists. Unset the current one first.",
                details={"current_base": current_base.code},
            )

    currency = await crud.create_currency(
        db,
        code=data.code,
        name=data.name,
        symbol=data.symbol,
        exchange_rate=data.exchange_rate,
        is_base_currency=data.is_base_currency,
        is_active=data.is_active,
    )
    return CurrencyResponse.model_validate(currency)


async def update_currency(
    db, currency_id: str, data: CurrencyUpdate
) -> CurrencyResponse:
    """Update an existing currency.

    Args:
        db: Async database session.
        currency_id: UUID string of the currency.
        data: Validated CurrencyUpdate payload.

    Returns:
        CurrencyResponse schema.

    Raises:
        NotFoundError: If the currency does not exist.
        ValidationError: If setting a new base currency when one already exists.
    """
    currency = await crud.get_currency_by_id(db, currency_id)
    if currency is None:
        raise NotFoundError(message="Currency not found")

    # If promoting to base currency, ensure no other base exists
    if data.is_base_currency is True and not currency.is_base_currency:
        current_base = await crud.get_base_currency(db)
        if current_base is not None and current_base.id != currency_id:
            raise ValidationError(
                message="A base currency already exists. Unset the current one first.",
                details={"current_base": current_base.code},
            )

    update_data = data.model_dump(exclude_unset=True)
    updated = await crud.update_currency(db, currency_id, **update_data)
    return CurrencyResponse.model_validate(updated)
