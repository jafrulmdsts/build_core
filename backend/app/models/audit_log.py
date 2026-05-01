import uuid

from sqlalchemy import Column, String, DateTime, Text, func

from app.database import Base as DBBase


class AuditLog(DBBase):
    """Immutable audit trail — records every significant action.

    This table does NOT inherit from BaseModel because it intentionally
    has no updated_at (immutable records) and no deleted_at (never soft-deleted).
    """

    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    organization_id = Column(String(36), nullable=True)
    user_id = Column(String(36), nullable=True)
    action = Column(String(50), nullable=False)
    table_name = Column(String(100), nullable=True)
    record_id = Column(String(36), nullable=True)
    old_values = Column(Text, nullable=True)
    new_values = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
