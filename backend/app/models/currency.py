"""
Currency Model.

Stores supported currencies with exchange rates against a base currency.
No foreign keys — references are soft string IDs validated at service layer.
"""

from sqlalchemy import Column, String, Boolean, Numeric
from app.models.base import BaseModel


class Currency(BaseModel):
    __tablename__ = "currencies"

    code = Column(String(3), nullable=False, unique=True)  # ISO 4217: BDT, USD, EUR
    name = Column(String(100), nullable=False)
    symbol = Column(String(10), nullable=False)  # ৳, $, €
    exchange_rate = Column(Numeric(12, 6), default=1.0)  # Against base currency
    is_base_currency = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
