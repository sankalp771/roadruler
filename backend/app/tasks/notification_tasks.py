import logging
import smtplib
from email.message import EmailMessage
from urllib.parse import quote

import httpx

from app.core.celery_app import celery_app
from app.core.config import settings

logger = logging.getLogger(__name__)


def lookup_clerk_email(user_id: str) -> str | None:
    if not settings.CLERK_SECRET_KEY:
        return None
    url = f"{settings.CLERK_API_BASE_URL.rstrip('/')}/users/{quote(user_id, safe='')}"
    response = httpx.get(url, headers={"Authorization": f"Bearer {settings.CLERK_SECRET_KEY}"}, timeout=10.0)
    response.raise_for_status()
    user = response.json()
    primary_id = user.get("primary_email_address_id")
    emails = user.get("email_addresses") or []
    primary = next((item.get("email_address") for item in emails if item.get("id") == primary_id), None)
    return primary or (emails[0].get("email_address") if emails else None)


def send_status_email(recipient: str, complaint_id: str, previous_status: str, new_status: str) -> None:
    if not all((settings.SMTP_HOST, settings.SMTP_FROM_EMAIL)):
        raise RuntimeError("SMTP_HOST and SMTP_FROM_EMAIL must be configured to send notification email")
    message = EmailMessage()
    message["Subject"] = f"RoadRuler report status: {new_status.replace('_', ' ').title()}"
    message["From"] = settings.SMTP_FROM_EMAIL
    message["To"] = recipient
    message.set_content(
        f"Your RoadRuler report {complaint_id} changed from "
        f"{previous_status.replace('_', ' ').lower()} to {new_status.replace('_', ' ').lower()}."
    )
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as smtp:
        if settings.SMTP_STARTTLS:
            smtp.starttls()
        if settings.SMTP_USERNAME:
            smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        smtp.send_message(message)


@celery_app.task(
    name="app.tasks.notification_tasks.send_status_update_email",
    bind=True,
    max_retries=3,
    default_retry_delay=30,
)
def send_status_update_email(self, user_id: str, complaint_id: str, previous_status: str, new_status: str):
    """Deliver status emails asynchronously; in-app notifications are already durable."""
    if not settings.SMTP_HOST or not settings.SMTP_FROM_EMAIL:
        logger.warning("Status email skipped: SMTP is not configured (complaint %s)", complaint_id)
        return {"status": "skipped", "reason": "smtp_not_configured", "complaint_id": complaint_id}
    try:
        recipient = lookup_clerk_email(user_id)
        if not recipient:
            logger.warning("Status email skipped: Clerk has no email for user %s", user_id)
            return {"status": "skipped", "reason": "recipient_unavailable", "complaint_id": complaint_id}
        send_status_email(recipient, complaint_id, previous_status, new_status)
        logger.info("Status email sent for complaint %s", complaint_id)
        return {"status": "sent", "complaint_id": complaint_id}
    except (httpx.HTTPError, smtplib.SMTPException, OSError) as exc:
        logger.exception("Status email delivery failed for complaint %s", complaint_id)
        raise self.retry(exc=exc)
