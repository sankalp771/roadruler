from sqlalchemy import Column, Integer, String
from geoalchemy2 import Geometry

from app.db.base import Base


class WardBoundary(Base):
    """Configured municipal jurisdiction polygon used for complaint routing."""

    __tablename__ = "ward_boundaries"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    department_name = Column(String, nullable=False)
    priority = Column(Integer, nullable=False, default=0, server_default="0")
    geom = Column(Geometry(geometry_type="MULTIPOLYGON", srid=4326), nullable=False)
