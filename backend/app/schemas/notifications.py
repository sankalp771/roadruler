from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    complaint_id: str
    message: str
    is_read: bool
    created_at: datetime


class NotificationPage(BaseModel):
    items: list[NotificationRead]
    unread_count: int
