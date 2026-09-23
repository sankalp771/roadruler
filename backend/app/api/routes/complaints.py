from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, status, HTTPException
from sqlalchemy.orm import Session
from geoalchemy2.elements import WKTElement
import logging

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.complaint import Complaint
from app.services.storage import upload_file_to_supabase

router = APIRouter()

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_complaint(
    latitude: float = Form(...),
    longitude: float = Form(...),
    category: str = Form(...),
    description: Optional[str] = Form(None),
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Read file bytes
        file_bytes = await file.read()
        
        # Upload to Supabase Storage
        image_url = upload_file_to_supabase(file_bytes, file.filename)
        
        # Create PostGIS point
        location = WKTElement(f'POINT({longitude} {latitude})', srid=4326)
        
        # Save to database
        new_complaint = Complaint(
            user_id=current_user["user_id"],
            category=category,
            description=description,
            image_url=image_url,
            location=location,
            status="RECEIVED",
            severity_level="PENDING"
        )
        
        db.add(new_complaint)
        db.commit()
        db.refresh(new_complaint)
        
        return {
            "id": new_complaint.id,
            "status": new_complaint.status,
            "image_url": new_complaint.image_url,
            "location": {"lat": latitude, "lng": longitude}
        }
        
    except Exception as e:
        db.rollback()
        logging.error(f"Error creating complaint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
