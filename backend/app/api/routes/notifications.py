import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.notification import Notification
from app.schemas.notifications import NotificationPage, NotificationRead

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("", response_model=NotificationPage)
def list_notifications(
    unread_only: bool = Query(False),
    limit: int = Query(20, ge=1, le=50),
    offset: int = Query(0, ge=0),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    base_query = db.query(Notification).filter(Notification.user_id == user["user_id"])
    unread_count = base_query.filter(Notification.is_read.is_(False)).count()
    query = base_query
    if unread_only:
        query = query.filter(Notification.is_read.is_(False))
    rows = query.order_by(Notification.created_at.desc(), Notification.id.desc()).offset(offset).limit(limit).all()
    return NotificationPage(items=rows, unread_count=unread_count)


@router.post("/{notification_id}/read", response_model=NotificationRead)
def mark_notification_read(
    notification_id: str,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    notification = (
        db.query(Notification)
        .filter(Notification.id == notification_id, Notification.user_id == user["user_id"])
        .with_for_update()
        .first()
    )
    if notification is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    if not notification.is_read:
        notification.is_read = True
        try:
            db.commit()
            db.refresh(notification)
        except Exception as exc:
            db.rollback()
            logger.exception("Failed to mark notification %s as read", notification_id)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not update notification") from exc
    return notification
