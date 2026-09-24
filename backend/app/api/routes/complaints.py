from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, status, HTTPException, Query
from sqlalchemy import func, cast
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from geoalchemy2.elements import WKTElement
from geoalchemy2 import Geography
import logging

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.complaint import Complaint
from app.models.complaint_upvote import ComplaintUpvote
from app.schemas.complaint import ComplaintRead, ComplaintLocation, NearbyComplaintRead, ComplaintUpvoteRead
from app.services.storage import delete_file_from_supabase, upload_file_to_supabase
from app.tasks.ai_tasks import process_complaint_ai_task

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/{complaint_id}/upvote", response_model=ComplaintUpvoteRead)
def upvote_complaint(
    complaint_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add one support vote per citizen to an open complaint."""
    complaint = (
        db.query(Complaint)
        .filter(Complaint.id == complaint_id)
        .with_for_update()
        .first()
    )
    if complaint is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")
    if complaint.status in {"RESOLVED", "CANCELLED"}:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Complaint is no longer open")

    db.add(ComplaintUpvote(complaint_id=complaint_id, user_id=current_user["user_id"]))
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already supported this complaint",
        ) from exc

    complaint.upvote_count = (complaint.upvote_count or 0) + 1
    try:
        db.commit()
        db.refresh(complaint)
    except Exception:
        db.rollback()
        logger.exception("Failed to record upvote for complaint %s", complaint_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not record upvote")

    return ComplaintUpvoteRead(
        complaint_id=complaint.id,
        upvote_count=complaint.upvote_count,
        message="Upvote recorded successfully",
    )


@router.get("/nearby", response_model=list[NearbyComplaintRead])
def read_nearby_complaints(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    radius_meters: float = Query(15.0, gt=0, le=1000),
    _current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Find active complaints within a physical distance of the selected point."""
    point = func.ST_SetSRID(func.ST_MakePoint(longitude, latitude), 4326)
    distance = func.ST_Distance(cast(Complaint.location, Geography), cast(point, Geography))
    rows = (
        db.query(
            Complaint,
            func.ST_Y(Complaint.location).label("latitude"),
            func.ST_X(Complaint.location).label("longitude"),
            distance.label("distance_meters"),
        )
        .filter(
            func.ST_DWithin(cast(Complaint.location, Geography), cast(point, Geography), radius_meters),
            Complaint.status.notin_(("RESOLVED", "CANCELLED")),
            Complaint.user_id != _current_user["user_id"],
        )
        .order_by(distance.asc())
        .limit(100)
        .all()
    )
    return [
        NearbyComplaintRead(
            id=row[0].id,
            category=row[0].category,
            ai_category=row[0].ai_category,
            image_url=row[0].image_url,
            status=row[0].status,
            upvote_count=row[0].upvote_count,
            location=ComplaintLocation(lat=row.latitude, lng=row.longitude),
            distance_meters=row.distance_meters,
        )
        for row in rows
    ]


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
        is_supporter = (
            db.query(ComplaintUpvote.complaint_id)
            .filter(
                ComplaintUpvote.complaint_id == complaint_id,
                ComplaintUpvote.user_id == current_user["user_id"],
            )
            .first()
        )
        if is_supporter is not None:
            row = (
                db.query(
                    Complaint,
                    func.ST_Y(Complaint.location),
                    func.ST_X(Complaint.location),
                )
                .filter(Complaint.id == complaint_id)
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
        detection_details=complaint.detection_details,
        duplicate_of_id=complaint.duplicate_of_id,
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
