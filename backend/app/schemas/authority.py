from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.schemas.complaint import ComplaintLocation


class AuthorityComplaintRead(BaseModel):
    id: str
    category: str
    ai_category: Optional[str] = None
    description: Optional[str] = None
    image_url: str
    severity_score: float
    severity_level: str
    status: str
    upvote_count: int
    ward_id: Optional[str] = None
    location: ComplaintLocation
    created_at: Optional[datetime] = None


class AuthorityComplaintPage(BaseModel):
    items: list[AuthorityComplaintRead]
    total: int
    page: int
    limit: int
    pages: int
