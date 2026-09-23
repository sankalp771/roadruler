from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_current_user
from app.db.session import get_db
from app.main import app


class FakeQuery:
    def __init__(self, complaint):
        self.complaint = complaint

    def filter(self, *conditions):
        for condition in conditions:
            field = getattr(condition.left, "name", None)
            expected = getattr(condition.right, "value", None)
            if field and getattr(self.complaint, field, None) != expected:
                self.complaint = None
        return self

    def first(self):
        if self.complaint is None:
            return None
        return self.complaint, 19.076, 72.8777


class FakeDb:
    def __init__(self, complaint):
        self.complaint = complaint

    def query(self, *_entities):
        return FakeQuery(self.complaint)


@pytest.fixture()
def complaint_client():
    complaint = SimpleNamespace(
        id="complaint-123",
        user_id="citizen-1",
        category="POTHOLE",
        ai_category="Pothole",
        description="Deep pothole near the junction",
        image_url="https://storage.example/complaint.jpg",
        severity_score=84.5,
        severity_level="CRITICAL",
        detections_count=3,
        status="RECEIVED",
        upvote_count=1,
        created_at=datetime(2026, 9, 23, tzinfo=timezone.utc),
    )
    app.dependency_overrides[get_current_user] = lambda: {"user_id": "citizen-1"}
    app.dependency_overrides[get_db] = lambda: FakeDb(complaint)
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.pop(get_current_user, None)
    app.dependency_overrides.pop(get_db, None)


def test_owner_can_read_complaint_with_location(complaint_client):
    response = complaint_client.get("/api/v1/complaints/complaint-123")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == "complaint-123"
    assert body["status"] == "RECEIVED"
    assert body["ai_category"] == "Pothole"
    assert body["detections_count"] == 3
    assert body["location"] == {"lat": 19.076, "lng": 72.8777}


def test_complaint_read_returns_not_found_for_another_owner(complaint_client):
    app.dependency_overrides[get_current_user] = lambda: {"user_id": "citizen-2"}

    response = complaint_client.get("/api/v1/complaints/complaint-123")

    assert response.status_code == 404
    assert response.json()["detail"] == "Complaint not found"
