import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.sql import func

from app.db.base import Base


class ComplaintAction(Base):
    """Immutable record of each authority status transition and its work-order notes."""

    __tablename__ = "complaint_actions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    complaint_id = Column(String, ForeignKey("complaints.id", ondelete="CASCADE"), nullable=False, index=True)
    actor_user_id = Column(String, nullable=False)
    previous_status = Column(String, nullable=False)
    new_status = Column(String, nullable=False)
    contractor_name = Column(String(120), nullable=True)
    notes = Column(Text, nullable=True)
    resolution_image_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
