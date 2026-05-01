"""
File Attachment Model.

Stores metadata for files uploaded against any entity type
(project, employee, contractor, expense). Does NOT inherit from
BaseModel — files are managed by storage and soft-delete doesn't
apply well to file records.
"""

import uuid

from sqlalchemy import Column, String, DateTime, Text, Integer, func

from app.database import Base as DBBase


class FileAttachment(DBBase):
    __tablename__ = "file_attachments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    organization_id = Column(String(36), nullable=False)
    entity_type = Column(String(50), nullable=False)  # project, employee, contractor, expense
    entity_id = Column(String(36), nullable=False)
    file_name = Column(String(255), nullable=False)  # logical name (reg-based)
    original_name = Column(String(255), nullable=True)  # uploaded file name
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=True)  # image, document, pdf
    mime_type = Column(String(100), nullable=True)
    file_size = Column(Integer, nullable=True)  # bytes
    uploaded_by = Column(String(36), nullable=True)
