from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, status, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from geoalchemy2.elements import WKTElement
import logging

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.complaint import Complaint
from app.schemas.complaint import ComplaintRead, ComplaintLocation
from app.services.storage import delete_file_from_supabase, upload_file_to_supabase
from app.tasks.ai_tasks import process_complaint_ai_task

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/{complaint_id}", response_model=ComplaintRead)
def read_complaint(
    complaint_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the signed-in citizen's complaint and its current AI/status data."""
    row = (
        db.query(
            Complaint,
            func.ST_Y(Complaint.location),
            func.ST_X(Complaint.location),
        )
        .filter(
            Complaint.id == complaint_id,
            Complaint.user_id == current_user["user_id"],
        )
        .first()
    )
    if row is None:
        # Do not reveal whether another citizen owns the supplied ID.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")

    complaint, latitude, longitude = row
    return ComplaintRead(
        id=complaint.id,
        category=complaint.category,
        ai_category=complaint.ai_category,
        description=complaint.description,
        image_url=complaint.image_url,
        severity_score=complaint.severity_score,
        severity_level=complaint.severity_level,
        detections_count=complaint.detections_count,
        status=complaint.status,
        upvote_count=complaint.upvote_count,
        location=ComplaintLocation(lat=latitude, lng=longitude),
        created_at=complaint.created_at,
    )

@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def create_complaint(
    latitude: float = Form(...),
    longitude: float = Form(...),
    category: str = Form(...),
    description: Optional[str] = Form(None),
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Accept a citizen complaint, store the raw record with status PROCESSING,
    and dispatch AI severity analysis to the Celery worker queue (Day 6).
    Returns 202 Accepted immediately; the worker enriches the row afterwards.
    """
    if latitude < -90 or latitude > 90 or longitude < -180 or longitude > 180:
        raise HTTPException(status_code=422, detail="Invalid latitude/longitude values")

    image_url = None
    operation = "read upload"
    try:
        # Read file bytes
        file_bytes = await file.read()
        if not file_bytes:
            raise HTTPException(status_code=422, detail="Uploaded file is empty")

        # Upload to Supabase Storage
        operation = "upload image to storage"
        image_url = upload_file_to_supabase(file_bytes, file.filename, file.content_type)

        # Create PostGIS point
        operation = "construct PostGIS point"
        location = WKTElement(f'POINT({longitude} {latitude})', srid=4326)

        # Save raw complaint; AI enrichment happens asynchronously
        operation = "construct complaint record"
        new_complaint = Complaint(
            user_id=current_user["user_id"],
            category=category,
            description=description,
            image_url=image_url,
            location=location,
            status="PROCESSING",
            severity_level="PENDING",
            detections_count=0,
        )

        operation = "add complaint record to database session"
        db.add(new_complaint)
        operation = "persist complaint"
        db.commit()
        operation = "refresh complaint record"
        db.refresh(new_complaint)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        if image_url:
            try:
                delete_file_from_supabase(image_url)
            except Exception as cleanup_error:
                logger.error("Failed to remove orphaned complaint image: %s", cleanup_error)
        logger.exception("Complaint creation failed during %s: %s", operation, e)
        raise HTTPException(status_code=500, detail="Internal server error")

    # Dispatch AFTER the commit so the worker can always see the row.
    # A queue outage must not lose the complaint — log and continue.
    try:
        process_complaint_ai_task.delay(new_complaint.id)
    except Exception as e:
        logger.error(f"Failed to dispatch AI task for complaint {new_complaint.id}: {str(e)}")

    return {
        "id": new_complaint.id,
        "status": new_complaint.status,
        "severity_level": new_complaint.severity_level,
        "detections_count": new_complaint.detections_count,
        "image_url": new_complaint.image_url,
        "location": {"lat": latitude, "lng": longitude}
    }
