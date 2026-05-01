import uuid

from sqlalchemy import Column, String, DateTime, Boolean, Text, func

from app.database import Base as DBBase


class UserPermissionOverride(DBBase):
    """Per-user permission overrides (grant or revoke specific permissions).

    This table does NOT use soft delete (deleted_at) because overrides
    are meant to be explicit and auditable — they are hard-deleted
    when no longer needed.
    """

    __tablename__ = "user_permission_overrides"

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
    user_id = Column(String(36), nullable=False)
    permission_key = Column(String(200), nullable=False)
    is_granted = Column(Boolean, nullable=False)
    granted_by = Column(String(36), nullable=True)
    reason = Column(Text, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
