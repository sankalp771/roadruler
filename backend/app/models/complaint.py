import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
from app.db.base import Base

class Complaint(Base):
    __tablename__ = 'complaints'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    description = Column(String, nullable=False)
    category = Column(String, nullable=False)
    location = Column(Geometry(geometry_type='POINT', srid=4326), nullable=False)
    status = Column(String, default="Received")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
