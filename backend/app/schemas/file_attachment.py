"""
File Attachment Pydantic Schemas.

Request/response schemas for file attachment records.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class FileAttachmentCreate(BaseModel):
    entity_type: str = Field(..., max_length=50)
    entity_id: str
    file_name: str = Field(..., max_length=255)
    original_name: str | None = Field(None, max_length=255)
    file_path: str = Field(..., max_length=500)
    file_type: str | None = Field(None, max_length=50)
    mime_type: str | None = Field(None, max_length=100)
    file_size: int | None = None
    uploaded_by: str | None = None


class FileAttachmentResponse(BaseModel):
    id: str
    organization_id: str
    entity_type: str
    entity_id: str
    file_name: str
    original_name: str | None = None
    file_path: str
    file_type: str | None = None
    mime_type: str | None = None
    file_size: int | None = None
    uploaded_by: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
