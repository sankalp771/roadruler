from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.sql import func

from app.db.base import Base


class ComplaintUpvote(Base):
    __tablename__ = "complaint_upvotes"
    complaint_id = Column(
        String,
        ForeignKey("complaints.id", ondelete="CASCADE"),
        primary_key=True,
    )
    user_id = Column(String, primary_key=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
