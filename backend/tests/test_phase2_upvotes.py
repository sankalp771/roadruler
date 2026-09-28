import uuid

from geoalchemy2.elements import WKTElement

from app.db.session import SessionLocal
from app.models.complaint import Complaint
from app.models.complaint_upvote import ComplaintUpvote


def test_open_complaint_can_be_upvoted_once_and_tracked_by_supporter(auth_client):
    complaint_id = str(uuid.uuid4())
    db = SessionLocal()
    complaint = Complaint(
        id=complaint_id,
        user_id="another-citizen",
        category="POTHOLE",
        image_url="https://example.invalid/road.jpg",
        location=WKTElement("POINT(72.8777 19.076)", srid=4326),
        status="RECEIVED",
        upvote_count=1,
    )
    try:
        db.add(complaint)
        db.commit()

        response = auth_client.post(f"/api/v1/complaints/{complaint_id}/upvote")
        assert response.status_code == 200, response.text
        assert response.json() == {
            "complaint_id": complaint_id,
            "upvote_count": 2,
            "message": "Upvote recorded successfully",
        }

        duplicate_response = auth_client.post(f"/api/v1/complaints/{complaint_id}/upvote")
        assert duplicate_response.status_code == 409
        assert duplicate_response.json()["detail"] == "You have already supported this complaint"

        tracked = auth_client.get(f"/api/v1/complaints/{complaint_id}")
        assert tracked.status_code == 200, tracked.text
        assert tracked.json()["upvote_count"] == 2

        db.refresh(complaint)
        assert complaint.upvote_count == 2
        assert db.query(ComplaintUpvote).filter_by(
            complaint_id=complaint_id,
            user_id="user_integration_test_phase1",
        ).count() == 1

        complaint.status = "RESOLVED"
        db.commit()
        resolved_response = auth_client.post(f"/api/v1/complaints/{complaint_id}/upvote")
        assert resolved_response.status_code == 409
        assert resolved_response.json()["detail"] == "Complaint is no longer open"
    finally:
        db.rollback()
        db.query(ComplaintUpvote).filter_by(complaint_id=complaint_id).delete()
        db.query(Complaint).filter_by(id=complaint_id).delete()
        db.commit()
        db.close()
