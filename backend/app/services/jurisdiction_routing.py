from typing import Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.ward_boundary import WardBoundary


def resolve_jurisdiction(db: Session, longitude: float, latitude: float) -> Tuple[Optional[str], Optional[str]]:
    """Return the highest-priority configured jurisdiction covering a point.

    Boundary data is supplied by municipal GIS imports. If no polygon covers
    the point, preserve the complaint as unassigned instead of guessing an owner.
    """
    point = func.ST_SetSRID(func.ST_MakePoint(longitude, latitude), 4326)
    boundary = (
        db.query(WardBoundary)
        .filter(func.ST_Intersects(WardBoundary.geom, point))
        .order_by(WardBoundary.priority.desc(), WardBoundary.id.asc())
        .first()
    )
    if boundary is None:
        return None, None
    return boundary.id, boundary.department_name
