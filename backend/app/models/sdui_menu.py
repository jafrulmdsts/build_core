import uuid

from sqlalchemy import Column, String, DateTime, Boolean, Integer, func

from app.database import Base as DBBase


class SduiMenu(DBBase):
    """Server-driven UI menu items for dynamic navigation rendering.

    This table does NOT use soft delete (deleted_at). Menu items that are
    no longer needed are hard-deleted.
    """

    __tablename__ = "sdui_menus"

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
    parent_id = Column(String(36), nullable=True)
    label_key = Column(String(100), nullable=True)
    label_en = Column(String(100), nullable=False)
    label_bn = Column(String(100), nullable=False)
    icon = Column(String(100), nullable=True)
    route_path = Column(String(200), nullable=True)
    api_endpoint = Column(String(200), nullable=True)
    permission_key = Column(String(200), nullable=True)
    sort_order = Column(Integer, default=0)
    is_visible = Column(Boolean, default=True)
    target = Column(String(20), default="_self")
    menu_type = Column(String(20), default="sidebar")
