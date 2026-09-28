from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models.complaint import Complaint
from app.models.complaint_action import ComplaintAction
from app.models.notification import Notification


SLA_LIMITS = {
    "CRITICAL": timedelta(hours=48),
    "MODERATE": timedelta(days=7),
    "MINOR": timedelta(days=30),
}


def _as_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


def sla_deadline(created_at: Optional[datetime], severity_level: Optional[str]) -> Optional[datetime]:
    """Compute a UTC SLA deadline, or None while severity/timestamp is unavailable."""
    if created_at is None or not severity_level:
        return None
    duration = SLA_LIMITS.get(severity_level.upper())
    if duration is None:
        return None
    return _as_utc(created_at) + duration


def escalate_overdue_complaints(db: Session, now: Optional[datetime] = None) -> list[str]:
    """Escalate overdue active complaints exactly once and notify their owners."""
    current_time = _as_utc(now or datetime.now(timezone.utc))
    complaints = (
        db.query(Complaint)
        .filter(
            Complaint.status.notin_(("RESOLVED", "CANCELLED", "ESCALATED", "REJECTED")),
            Complaint.severity_level.in_(tuple(SLA_LIMITS)),
            Complaint.escalation_level == 0,
        )
        .with_for_update(skip_locked=True)
        .all()
    )
    escalated_ids = []
    for complaint in complaints:
        if complaint.escalation_level:
            continue
        deadline = sla_deadline(complaint.created_at, complaint.severity_level)
        if deadline is None or current_time <= deadline:
            continue
        previous_status = complaint.status
        complaint.status = "ESCALATED"
        complaint.escalation_level = (complaint.escalation_level or 0) + 1
        db.add(ComplaintAction(
            complaint_id=complaint.id,
            actor_user_id="system:sla-worker",
            previous_status=previous_status,
            new_status="ESCALATED",
            notes=f"Automatically escalated after {complaint.severity_level.lower()} SLA deadline.",
        ))
        db.add(Notification(
            user_id=complaint.user_id,
            complaint_id=complaint.id,
            message=f"Your road report {complaint.id} is overdue and has been escalated to the next authority level.",
        ))
        escalated_ids.append(complaint.id)
    db.commit()
    return escalated_ids
