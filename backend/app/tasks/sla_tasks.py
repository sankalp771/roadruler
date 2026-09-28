import logging

from app.core.celery_app import celery_app
from app.db.session import SessionLocal
from app.services.sla import escalate_overdue_complaints


logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.sla_tasks.check_sla_deadlines")
def check_sla_deadlines():
    """Run the scheduled SLA scan and persist escalations and notifications."""
    db = SessionLocal()
    try:
        complaint_ids = escalate_overdue_complaints(db)
        logger.info("SLA scan escalated %d complaints", len(complaint_ids))
        return {"escalated_count": len(complaint_ids), "complaint_ids": complaint_ids}
    except Exception:
        db.rollback()
        logger.exception("SLA deadline scan failed")
        raise
    finally:
        db.close()
