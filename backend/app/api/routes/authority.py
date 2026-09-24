from math import ceil
from typing import Literal, Optional

import logging
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.session import get_db
from app.models.complaint import Complaint
from app.models.complaint_action import ComplaintAction
from app.schemas.authority import AuthorityComplaintPage, AuthorityComplaintRead
from app.schemas.authority_actions import ComplaintStatusActionRead, ComplaintStatusUpdate
from app.schemas.complaint import ComplaintLocation
from app.services.authority_query import build_complaint_filters
from app.services.storage import upload_file_to_supabase

router = APIRouter()
authority_user = require_roles(["WARD_OFFICER", "ADMIN"])
logger = logging.getLogger(__name__)
ALLOWED_TRANSITIONS = {
    "RECEIVED": {"ASSIGNED"},
    "ASSIGNED": {"IN_REPAIR"},
    "IN_REPAIR": {"RESOLVED"},
}


@router.get("/complaints", response_model=AuthorityComplaintPage)
def list_authority_complaints(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status", min_length=1, max_length=32),
    severity: Optional[str] = Query(None, min_length=1, max_length=32),
    ward_id: Optional[str] = Query(None, min_length=1, max_length=64),
    category: Optional[str] = Query(None, min_length=1, max_length=64),
    search: Optional[str] = Query(None, min_length=1, max_length=100),
    sla_state: Optional[Literal["WITHIN_SLA", "OVERDUE"]] = None,
    _user: dict = Depends(authority_user),
    db: Session = Depends(get_db),
):
    filters = build_complaint_filters(
        status=status_filter,
        severity=severity,
        ward_id=ward_id,
        category=category,
        search=search,
        sla_state=sla_state,
    )
    query = db.query(Complaint).filter(filters)

    total = query.count()
    rows = (
        query.order_by(Complaint.severity_score.desc().nullslast(), Complaint.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )
    locations = {
        row.id: row
        for row in db.query(
            Complaint.id,
            func.ST_Y(Complaint.location).label("latitude"),
            func.ST_X(Complaint.location).label("longitude"),
        ).filter(Complaint.id.in_([complaint.id for complaint in rows])).all()
    }
    items = [
        AuthorityComplaintRead(
            id=complaint.id,
            category=complaint.category,
            ai_category=complaint.ai_category,
            description=complaint.description,
            image_url=complaint.image_url,
            severity_score=complaint.severity_score or 0,
            severity_level=complaint.severity_level or "PENDING",
            status=complaint.status,
            upvote_count=complaint.upvote_count or 0,
            ward_id=complaint.ward_id,
            location=ComplaintLocation(lat=locations[complaint.id].latitude, lng=locations[complaint.id].longitude),
            created_at=complaint.created_at,
        )
        for complaint in rows
    ]
    return AuthorityComplaintPage(items=items, total=total, page=page, limit=limit, pages=ceil(total / limit))


@router.patch("/complaints/{complaint_id}/status", response_model=ComplaintStatusActionRead)
def update_complaint_status(
    complaint_id: str,
    update: ComplaintStatusUpdate,
    current_user: dict = Depends(authority_user),
    db: Session = Depends(get_db),
):
    complaint = (
        db.query(Complaint)
        .filter(Complaint.id == complaint_id)
        .with_for_update()
        .first()
    )
    if complaint is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")
    if update.status not in ALLOWED_TRANSITIONS.get(complaint.status, set()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status transition")
    if update.status == "RESOLVED" and not update.resolution_image_url:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="resolution_image_url is required to resolve a complaint")
    if update.status != "RESOLVED" and update.resolution_image_url:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="resolution_image_url is only accepted when resolving a complaint")

    action = ComplaintAction(
        complaint_id=complaint.id,
        actor_user_id=current_user["user_id"],
        previous_status=complaint.status,
        new_status=update.status,
        contractor_name=update.contractor_name,
        notes=update.notes,
        resolution_image_url=update.resolution_image_url,
    )
    complaint.status = update.status
    db.add(action)
    try:
        db.commit()
        db.refresh(action)
    except Exception as exc:
        db.rollback()
        logger.exception("Failed to transition complaint %s to %s", complaint_id, update.status)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not update complaint status") from exc
    return {
        "id": action.id,
        "complaint_id": action.complaint_id,
        "previous_status": action.previous_status,
        "status": action.new_status,
        "contractor_name": action.contractor_name,
        "notes": action.notes,
        "resolution_image_url": action.resolution_image_url,
        "created_at": action.created_at,
    }


@router.post("/complaints/{complaint_id}/resolution-image")
def upload_resolution_image(
    complaint_id: str,
    file: UploadFile = File(...),
    _current_user: dict = Depends(authority_user),
    db: Session = Depends(get_db),
):
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if complaint is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")
    if complaint.status != "IN_REPAIR":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Resolution evidence can only be uploaded for complaints in repair")
    if file.content_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Only JPEG, PNG, and WebP images are supported")
    image_bytes = file.file.read(10 * 1024 * 1024 + 1)
    if not image_bytes or len(image_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Resolution image must be between 1 byte and 10 MB")
    try:
        image_url = upload_file_to_supabase(image_bytes, file.filename or "resolution.jpg", file.content_type)
    except Exception as exc:
        logger.exception("Failed to upload resolution evidence for complaint %s", complaint_id)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Could not store resolution evidence") from exc
    return {"resolution_image_url": image_url}
