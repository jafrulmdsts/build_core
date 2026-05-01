"""
SDUI Menu Pydantic schema for server-driven UI navigation.
"""

from datetime import datetime

from pydantic import BaseModel


class SduiMenuResponse(BaseModel):
    """Menu item data returned by the SDUI navigation API."""

    id: str
    parent_id: str | None = None
    label_key: str | None = None
    label_en: str
    label_bn: str
    icon: str | None = None
    route_path: str | None = None
    api_endpoint: str | None = None
    permission_key: str | None = None
    sort_order: int = 0
    is_visible: bool = True
    target: str = "_self"
    menu_type: str = "sidebar"
    children: list["SduiMenuResponse"] = Field(default_factory=list)
    created_at: datetime

    model_config = {"from_attributes": True}
