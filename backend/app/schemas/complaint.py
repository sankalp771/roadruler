from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ComplaintLocation(BaseModel):
    lat: float
    lng: float


class ComplaintRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    category: str
    ai_category: Optional[str] = None
    description: Optional[str] = None
    image_url: str
    severity_score: float
    severity_level: str
    detections_count: int = 0
    status: str
    upvote_count: int
    location: ComplaintLocation
    created_at: Optional[datetime] = None
