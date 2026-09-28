"""End-to-end Phase 2 API coverage against PostGIS and the real database."""

import uuid

from geoalchemy2.elements import WKTElement

from app.db.session import SessionLocal
from app.models.complaint import Complaint
from app.models.complaint_action import ComplaintAction
from app.models.complaint_upvote import ComplaintUpvote


def test_phase2_report_to_resolution_workflow(auth_client, authority_client, monkeypatch):
    complaint_ids = [str(uuid.uuid4()) for _ in range(3)]
    ward_id = f"PHASE2_{uuid.uuid4().hex[:10]}"
    coordinates = [
        (19.076, 72.8777),
        (19.07605, 72.8777),
        (19.076, 72.87775),
    ]
    db = SessionLocal()
    complaints = [
        Complaint(
            id=complaint_id,
            user_id="phase2_integration_reporter",
            category="PHASE2_TEST_POTHOLE",
            ai_category="Pothole",
            description=f"Phase 2 integration fixture {complaint_id}",
            image_url="https://example.invalid/phase2-fixture.jpg",
            severity_score=88,
            severity_level="CRITICAL",
            location=WKTElement(f"POINT({longitude} {latitude})", srid=4326),
            status="RECEIVED",
            upvote_count=1,
            ward_id=ward_id,
        )
        for complaint_id, (latitude, longitude) in zip(complaint_ids, coordinates)
    ]
    try:
        db.add_all(complaints)
        db.commit()

        nearby = auth_client.get(
            "/api/v1/complaints/nearby",
            params={"latitude": 19.076, "longitude": 72.8777, "radius_meters": 50},
        )
        assert nearby.status_code == 200, nearby.text
        nearby_ids = {item["id"] for item in nearby.json()}
        assert set(complaint_ids).issubset(nearby_ids)

        upvote = auth_client.post(f"/api/v1/complaints/{complaint_ids[0]}/upvote")
        assert upvote.status_code == 200, upvote.text
        assert upvote.json()["upvote_count"] == 2
        assert auth_client.post(f"/api/v1/complaints/{complaint_ids[0]}/upvote").status_code == 409

        queue = authority_client.get(
            "/api/v1/authority/complaints",
            params={
                "page": 1,
                "limit": 10,
                "ward_id": ward_id,
                "severity": "CRITICAL",
                "category": "PHASE2_TEST_POTHOLE",
                "search": "Phase 2 integration fixture",
                "sla_state": "WITHIN_SLA",
            },
        )
        assert queue.status_code == 200, queue.text
        assert {item["id"] for item in queue.json()["items"]} == set(complaint_ids)

        hotspots = authority_client.get("/api/v1/analytics/hotspots")
        assert hotspots.status_code == 200, hotspots.text
        assert hotspots.json()["type"] == "FeatureCollection"
        assert any(feature["properties"]["complaint_count"] >= 3 for feature in hotspots.json()["features"])

        assigned = authority_client.patch(
            f"/api/v1/authority/complaints/{complaint_ids[0]}/status",
            json={"status": "ASSIGNED", "contractor_name": "Phase 2 Test Contractor", "notes": "Dispatch crew"},
        )
        assert assigned.status_code == 200, assigned.text
        assert assigned.json()["previous_status"] == "RECEIVED"
        assert assigned.json()["status"] == "ASSIGNED"

        invalid_jump = authority_client.patch(
            f"/api/v1/authority/complaints/{complaint_ids[0]}/status",
            json={"status": "RESOLVED", "resolution_image_url": "https://example.invalid/fixed.jpg"},
        )
        assert invalid_jump.status_code == 400
        assert invalid_jump.json()["detail"] == "Invalid status transition"

        in_repair = authority_client.patch(
            f"/api/v1/authority/complaints/{complaint_ids[0]}/status",
            json={"status": "IN_REPAIR", "notes": "Repair started"},
        )
        assert in_repair.status_code == 200, in_repair.text
        monkeypatch.setattr(
            "app.api.routes.authority.upload_file_to_supabase",
            lambda image_bytes, filename, content_type: "https://storage.example.org/phase2-resolution.jpg",
        )
        evidence = authority_client.post(
            f"/api/v1/authority/complaints/{complaint_ids[0]}/resolution-image",
            files={"file": ("resolution.jpg", b"test-image-bytes", "image/jpeg")},
        )
        assert evidence.status_code == 200, evidence.text
        resolution_url = evidence.json()["resolution_image_url"]
        missing_proof = authority_client.patch(
            f"/api/v1/authority/complaints/{complaint_ids[0]}/status",
            json={"status": "RESOLVED"},
        )
        assert missing_proof.status_code == 422
        resolved = authority_client.patch(
            f"/api/v1/authority/complaints/{complaint_ids[0]}/status",
            json={"status": "RESOLVED", "resolution_image_url": resolution_url, "notes": "Repair verified"},
        )
        assert resolved.status_code == 200, resolved.text
        assert resolved.json()["status"] == "RESOLVED"
        assert auth_client.post(f"/api/v1/complaints/{complaint_ids[0]}/upvote").status_code == 409

        history = db.query(ComplaintAction).filter(ComplaintAction.complaint_id == complaint_ids[0]).order_by(ComplaintAction.created_at).all()
        assert [action.new_status for action in history] == ["ASSIGNED", "IN_REPAIR", "RESOLVED"]
    finally:
        db.rollback()
        db.query(ComplaintAction).filter(ComplaintAction.complaint_id.in_(complaint_ids)).delete(synchronize_session=False)
        db.query(ComplaintUpvote).filter(ComplaintUpvote.complaint_id.in_(complaint_ids)).delete(synchronize_session=False)
        db.query(Complaint).filter(Complaint.id.in_(complaint_ids)).delete(synchronize_session=False)
        db.commit()
        db.close()
