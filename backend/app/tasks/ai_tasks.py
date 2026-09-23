"""
Asynchronous AI enrichment tasks (Day 6).
The HTTP layer stores a raw complaint with status 'PROCESSING' and hands
the heavy YOLO inference to a Celery worker via this task.
"""

import logging

import httpx

from app.core.celery_app import celery_app
from app.db.session import SessionLocal
from app.models.complaint import Complaint
from app.services.ai_service import analyze_image

logger = logging.getLogger(__name__)


def _fetch_image_bytes(image_url: str) -> bytes:
    """Download the complaint image from Supabase public storage."""
    response = httpx.get(image_url, timeout=30.0, follow_redirects=True)
    response.raise_for_status()
    if not response.content:
        raise ValueError(f"Empty image body downloaded from {image_url}")
    return response.content


@celery_app.task(
    name="app.tasks.ai_tasks.process_complaint_ai_task",
    bind=True,
    max_retries=3,
    default_retry_delay=10,
)
def process_complaint_ai_task(self, complaint_id: str):
    """
    Fetch the complaint image, run AI severity analysis, and persist the
    enrichment back onto the complaint row. Retries transient failures
    (network / DB hiccups) up to 3 times with a 10s delay.
    """
    db = SessionLocal()
    try:
        complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
        if complaint is None:
            logger.error(f"Complaint {complaint_id} not found; dropping AI task.")
            return {"complaint_id": complaint_id, "status": "NOT_FOUND"}

        image_bytes = _fetch_image_bytes(complaint.image_url)
        ai_result = analyze_image(image_bytes)

        complaint.ai_category = ai_result["ai_category"]
        complaint.severity_score = ai_result["severity_score"]
        complaint.severity_level = ai_result["severity_level"]
        complaint.detections_count = ai_result["detections_count"]
        complaint.status = "RECEIVED"
        db.commit()

        logger.info(
            f"Complaint {complaint_id} enriched: "
            f"{ai_result['severity_level']} ({ai_result['severity_score']})"
        )
        return {
            "complaint_id": complaint_id,
            "status": "RECEIVED",
            **ai_result,
        }
    except Exception as exc:
        db.rollback()
        logger.exception(f"AI processing failed for complaint {complaint_id}: {exc}")
        try:
            raise self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            # Final failure: release the complaint into the normal flow
            # un-enriched instead of leaving it stuck in PROCESSING.
            complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
            if complaint is not None:
                complaint.status = "RECEIVED"
                complaint.severity_level = "PENDING"
                db.commit()
            return {"complaint_id": complaint_id, "status": "AI_FAILED"}
    finally:
        db.close()
