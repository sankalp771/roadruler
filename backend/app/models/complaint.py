import uuid
from sqlalchemy import Column, String, DateTime, Float, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
try:
    from geoalchemy2 import Geometry
    location_column = Column(Geometry(geometry_type='POINT', srid=4326), nullable=False)
except ImportError:
    location_column = Column(String, nullable=True)
from app.db.base import Base

class Complaint(Base):
    __tablename__ = 'complaints'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    category = Column(String, nullable=False)
    description = Column(Text)
    image_url = Column(String, nullable=False)
    severity_score = Column(Float, default=0.0)
    severity_level = Column(String, default="PENDING")
    status = Column(String, default="RECEIVED")
    upvote_count = Column(Integer, default=1)
    location = location_column
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
