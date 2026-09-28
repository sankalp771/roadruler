from datetime import datetime, timezone
from unittest.mock import Mock, patch

from app.db.session import get_db
from app.main import app
from app.api.routes.authority import update_complaint_status
from app.models.complaint_action import ComplaintAction
from app.models.notification import Notification
from app.schemas.authority_actions import ComplaintStatusUpdate
from app.services.notifications import create_status_notification
from app.tasks.notification_tasks import lookup_clerk_email, send_status_email


class FakeNotificationQuery:
    def __init__(self, row):
        self.row = row

    def filter(self, *_criteria):
        return self

    def count(self):
        return 1

    def order_by(self, *_criteria):
        return self

    def offset(self, _value):
        return self

    def limit(self, _value):
        return self

    def all(self):
        return [self.row]

    def with_for_update(self):
        return self

    def first(self):
        return self.row


def test_notification_list_and_read_endpoints_are_owner_authenticated(auth_client, monkeypatch):
    row = Notification(
        id="notice-1",
        user_id="user_integration_test_phase1",
        complaint_id="complaint-1",
        message="Report moved to assigned.",
        is_read=False,
        created_at=datetime(2026, 9, 29, tzinfo=timezone.utc),
    )
    db = Mock()
    db.query.return_value = FakeNotificationQuery(row)

    def override_db():
        yield db

    monkeypatch.setitem(app.dependency_overrides, get_db, override_db)
    try:
        listed = auth_client.get("/api/v1/notifications")
        marked = auth_client.post("/api/v1/notifications/notice-1/read")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert listed.status_code == 200
    assert listed.json()["unread_count"] == 1
    assert listed.json()["items"][0]["is_read"] is False
    assert marked.status_code == 200
    assert marked.json()["is_read"] is True
    db.commit.assert_called_once()


def test_status_notification_is_created_for_complaint_owner():
    db = Mock()
    complaint = Mock(id="complaint-7", user_id="citizen-7")

    notification = create_status_notification(db, complaint, "IN_REPAIR", "RESOLVED")

    assert notification.user_id == "citizen-7"
    assert notification.complaint_id == "complaint-7"
    assert "in repair" in notification.message and "resolved" in notification.message
    db.add.assert_called_once_with(notification)


def test_authority_status_change_persists_alert_and_queues_email():
    complaint = Mock(id="case-9", user_id="citizen-9", status="RECEIVED")
    query = FakeNotificationQuery(complaint)
    db = Mock()
    db.query.return_value = query
    db.refresh.side_effect = lambda action: setattr(action, "created_at", datetime(2026, 9, 29, tzinfo=timezone.utc))
    update = ComplaintStatusUpdate(status="ASSIGNED", notes="Crew scheduled")

    with patch("app.api.routes.authority.send_status_update_email.delay") as email_queue:
        response = update_complaint_status("case-9", update, {"user_id": "officer-1"}, db)

    added = [call.args[0] for call in db.add.call_args_list]
    assert len(added) == 2
    assert isinstance(added[0], ComplaintAction)
    assert isinstance(added[1], Notification)
    assert added[1].user_id == "citizen-9"
    assert "assigned" in added[1].message
    assert response["status"] == "ASSIGNED"
    email_queue.assert_called_once_with("citizen-9", "case-9", "RECEIVED", "ASSIGNED")


def test_clerk_email_lookup_uses_primary_address_and_bearer_auth(monkeypatch):
    response = Mock()
    response.json.return_value = {
        "primary_email_address_id": "email-2",
        "email_addresses": [
            {"id": "email-1", "email_address": "old@example.com"},
            {"id": "email-2", "email_address": "citizen@example.com"},
        ],
    }
    monkeypatch.setattr("app.tasks.notification_tasks.settings.CLERK_SECRET_KEY", "test-secret")
    with patch("app.tasks.notification_tasks.httpx.get", return_value=response) as get:
        result = lookup_clerk_email("user/7")
    assert result == "citizen@example.com"
    assert get.call_args.args[0].endswith("/users/user%2F7")
    assert get.call_args.kwargs["headers"]["Authorization"] == "Bearer test-secret"


def test_status_email_is_sent_using_configured_smtp(monkeypatch):
    smtp = Mock()
    smtp.__enter__ = Mock(return_value=smtp)
    smtp.__exit__ = Mock(return_value=False)
    monkeypatch.setattr("app.tasks.notification_tasks.settings.SMTP_HOST", "smtp.example.test")
    monkeypatch.setattr("app.tasks.notification_tasks.settings.SMTP_PORT", 587)
    monkeypatch.setattr("app.tasks.notification_tasks.settings.SMTP_USERNAME", "road-ruler")
    monkeypatch.setattr("app.tasks.notification_tasks.settings.SMTP_PASSWORD", "test-password")
    monkeypatch.setattr("app.tasks.notification_tasks.settings.SMTP_FROM_EMAIL", "updates@example.test")
    monkeypatch.setattr("app.tasks.notification_tasks.settings.SMTP_STARTTLS", True)
    with patch("app.tasks.notification_tasks.smtplib.SMTP", return_value=smtp) as smtp_factory:
        send_status_email("citizen@example.test", "case-2", "IN_REPAIR", "RESOLVED")
    smtp_factory.assert_called_once_with("smtp.example.test", 587, timeout=15)
    smtp.starttls.assert_called_once_with()
    smtp.login.assert_called_once_with("road-ruler", "test-password")
    sent = smtp.send_message.call_args.args[0]
    assert sent["To"] == "citizen@example.test"
    assert "Resolved" in sent["Subject"]
