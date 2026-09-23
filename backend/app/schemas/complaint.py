from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class ComplaintLocation(BaseModel):
    lat: float
    lng: float


class AIDetection(BaseModel):
    class_id: int
    class_name: str
    confidence: float
    bbox_normalized: Optional[List[float]] = None


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
    detection_details: Optional[List[AIDetection]] = None
    status: str
    upvote_count: int
    location: ComplaintLocation
    created_at: Optional[datetime] = None
