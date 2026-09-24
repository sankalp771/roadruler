from datetime import datetime
from typing import Literal, Optional
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator


class ComplaintStatusUpdate(BaseModel):
    status: Literal["ASSIGNED", "IN_REPAIR", "RESOLVED"]
    contractor_name: Optional[str] = Field(None, max_length=120)
    notes: Optional[str] = Field(None, max_length=2000)
    resolution_image_url: Optional[str] = Field(None, max_length=2048)

    @field_validator("contractor_name", "notes", mode="before")
    @classmethod
    def trim_optional_text(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator("contractor_name", "notes")
    @classmethod
    def reject_blank_text(cls, value):
        if value == "":
            return None
        return value

    @field_validator("resolution_image_url")
    @classmethod
    def validate_resolution_url(cls, value):
        if value is None:
            return value
        parsed = urlparse(value)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("resolution_image_url must be an HTTP(S) URL")
        return value


class ComplaintStatusActionRead(BaseModel):
    id: str
    complaint_id: str
    previous_status: str
    status: str
    contractor_name: Optional[str] = None
    notes: Optional[str] = None
    resolution_image_url: Optional[str] = None
    created_at: datetime
