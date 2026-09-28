from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.session import get_db
from app.models.complaint import Complaint

router = APIRouter()
authority_user = require_roles(["WARD_OFFICER", "ADMIN"])


@router.get("/hotspots")
def get_hotspots(_user: dict = Depends(authority_user), db: Session = Depends(get_db)):
    from ai_engine.clustering import cluster_coordinates
    from ai_engine.cluster_summary import summarize_cluster

    rows = (
        db.query(
            Complaint.id,
            Complaint.category,
            Complaint.ai_category,
            Complaint.severity_score,
            func.ST_Y(Complaint.location).label("latitude"),
            func.ST_X(Complaint.location).label("longitude"),
        )
        .filter(Complaint.status.notin_(("RESOLVED", "CANCELLED")))
        .all()
    )
    complaints = [
        {
            "id": row.id,
            "latitude": row.latitude,
            "longitude": row.longitude,
            "severity_score": row.severity_score or 0,
            "category": row.ai_category or row.category,
        }
        for row in rows
        if row.latitude is not None and row.longitude is not None
    ]
    labels = cluster_coordinates([(item["latitude"], item["longitude"]) for item in complaints])
    clusters: dict[int, list[dict]] = {}
    for label, complaint in zip(labels, complaints):
        if label >= 0:
            clusters.setdefault(label, []).append(complaint)

    features = []
    for cluster_id, members in clusters.items():
        summary = summarize_cluster(cluster_id, members)
        features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [summary["longitude"], summary["latitude"]]},
                "properties": {
                    "cluster_id": cluster_id,
                    "complaint_count": summary["complaint_count"],
                    "avg_severity": summary["avg_severity"],
                    "dominant_category": summary["dominant_category"],
                    "risk_level": summary["risk_level"],
                },
            }
        )
    return {"type": "FeatureCollection", "features": features}
