"""
Currency Pydantic Schemas.

Request/response schemas for the currency management feature.
"""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class CurrencyCreate(BaseModel):
    code: str = Field(..., max_length=3)
    name: str = Field(..., max_length=100)
    symbol: str = Field(..., max_length=10)
    exchange_rate: Decimal = Field(default=Decimal("1.0"))
    is_base_currency: bool = False
    is_active: bool = True


class CurrencyUpdate(BaseModel):
    name: str | None = Field(None, max_length=100)
    symbol: str | None = Field(None, max_length=10)
    exchange_rate: Decimal | None = None
    is_base_currency: bool | None = None
    is_active: bool | None = None


class CurrencyResponse(BaseModel):
    id: str
    code: str
    name: str
    symbol: str
    exchange_rate: Decimal = Decimal("1.0")
    is_base_currency: bool = False
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
