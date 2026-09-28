from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.models.complaint_action import ComplaintAction
from app.models.notification import Notification
from app.services.sla import escalate_overdue_complaints, sla_deadline
from app.core.celery_app import celery_app
from app.api.routes.authority import ALLOWED_TRANSITIONS


def test_sla_deadlines_follow_severity_policy_and_normalize_naive_dates():
    created_at = datetime(2026, 9, 1, tzinfo=timezone.utc)

    assert sla_deadline(created_at, "CRITICAL") == created_at + timedelta(hours=48)
    assert sla_deadline(created_at, "MODERATE") == created_at + timedelta(days=7)
    assert sla_deadline(created_at, "MINOR") == created_at + timedelta(days=30)
    assert sla_deadline(created_at.replace(tzinfo=None), "critical") == created_at + timedelta(hours=48)
    assert sla_deadline(None, "CRITICAL") is None
    assert sla_deadline(created_at, "PENDING") is None


def test_sla_scan_escalates_overdue_items_once_and_creates_action_and_notification():
    now = datetime(2026, 9, 29, tzinfo=timezone.utc)
    overdue = SimpleNamespace(
        id="complaint-overdue",
        user_id="citizen-1",
        status="IN_REPAIR",
        severity_level="CRITICAL",
        escalation_level=0,
        created_at=now - timedelta(hours=49),
    )
    within_sla = SimpleNamespace(
        id="complaint-current",
        user_id="citizen-2",
        status="RECEIVED",
        severity_level="CRITICAL",
        escalation_level=0,
        created_at=now - timedelta(hours=47),
    )
    previously_escalated = SimpleNamespace(
        id="complaint-escalated",
        user_id="citizen-3",
        status="ASSIGNED",
        severity_level="CRITICAL",
        escalation_level=1,
        created_at=now - timedelta(days=4),
    )
    db = MagicMock()
    db.query.return_value.filter.return_value.with_for_update.return_value.all.return_value = [
        overdue, within_sla, previously_escalated,
    ]
    email_dispatcher = MagicMock()

    escalated_ids = escalate_overdue_complaints(db, now=now, email_dispatcher=email_dispatcher)

    assert escalated_ids == ["complaint-overdue"]
    assert overdue.status == "ESCALATED"
    assert overdue.escalation_level == 1
    assert within_sla.status == "RECEIVED"
    assert previously_escalated.status == "ASSIGNED"
    assert [type(call.args[0]) for call in db.add.call_args_list] == [ComplaintAction, Notification]
    action, notification = [call.args[0] for call in db.add.call_args_list]
    assert (action.previous_status, action.new_status, action.actor_user_id) == (
        "IN_REPAIR", "ESCALATED", "system:sla-worker"
    )
    assert notification.user_id == "citizen-1"
    assert notification.complaint_id == "complaint-overdue"
    email_dispatcher.assert_called_once_with("citizen-1", "complaint-overdue", "IN_REPAIR", "ESCALATED")
    db.commit.assert_called_once_with()


def test_escalated_ticket_can_reenter_the_authority_workflow():
    assert ALLOWED_TRANSITIONS["ESCALATED"] == {"ASSIGNED"}


def test_celery_beat_schedules_sla_scan_twice_an_hour():
    entry = celery_app.conf.beat_schedule["check-sla-deadlines-every-30-minutes"]

    assert entry["task"] == "app.tasks.sla_tasks.check_sla_deadlines"
    assert entry["schedule"]._orig_minute == "*/30"
