import uuid

from sqlalchemy import Column, String, DateTime, Boolean, func

from app.database import Base as DBBase


class BaseModel(DBBase):
    """Abstract base model with common fields for all entities."""

    __abstract__ = True

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    deleted_at = Column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )
