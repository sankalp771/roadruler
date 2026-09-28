from sqlalchemy.orm import Session

from app.models.complaint import Complaint
from app.models.notification import Notification


def create_status_notification(
    db: Session,
    complaint: Complaint,
    previous_status: str,
    new_status: str,
) -> Notification:
    """Add a persistent citizen notification to the current status transaction."""
    notification = Notification(
        user_id=complaint.user_id,
        complaint_id=complaint.id,
        message=f"Your road report {complaint.id} changed from {previous_status.replace('_', ' ').lower()} to {new_status.replace('_', ' ').lower()}.",
    )
    db.add(notification)
    return notification
