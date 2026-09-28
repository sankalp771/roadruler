"""
Phase 1 Integration Test Pass (Day 7).
Covers: health probes, Clerk auth enforcement, PostGIS storage,
AI severity engine, Celery wiring, and the full async complaint lifecycle
(POST 202 -> PROCESSING -> worker task -> enriched RECEIVED row).
"""

import uuid

import pytest
from sqlalchemy import text

from app.core.celery_app import celery_app
from app.core.config import settings
from app.db.session import SessionLocal, check_db_connection
from app.models.complaint import Complaint
from app.tasks.ai_tasks import process_complaint_ai_task
from tests.conftest import TEST_USER_ID


# ---------------------------------------------------------------------------
# 1. Core API & health interfaces (Day 1)
# ---------------------------------------------------------------------------

class TestHealthAndCore:
    def test_root_endpoint(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert "message" in resp.json()

    def test_health_endpoint(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# 2. Clerk JWT auth enforcement (Day 2)
# ---------------------------------------------------------------------------

class TestAuthEnforcement:
    def test_complaint_creation_rejected_without_token(self, client):
        resp = client.post(
            "/api/v1/complaints",
            data={"latitude": "19.07", "longitude": "72.87", "category": "Pothole"},
            files={"file": ("x.jpg", b"fake", "image/jpeg")},
        )
        # HTTPBearer returns 403 when the Authorization header is absent
        assert resp.status_code in (401, 403)

    def test_complaint_creation_rejected_with_garbage_token(self, client):
        resp = client.post(
            "/api/v1/complaints",
            headers={"Authorization": "Bearer not-a-real-jwt"},
            data={"latitude": "19.07", "longitude": "72.87", "category": "Pothole"},
            files={"file": ("x.jpg", b"fake", "image/jpeg")},
        )
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# 3. Database & PostGIS layer (Day 3)
# ---------------------------------------------------------------------------

class TestDatabaseLayer:
    def test_neon_connection_alive(self):
        assert check_db_connection() is True

    def test_postgis_extension_active(self):
        db = SessionLocal()
        try:
            version = db.execute(text("SELECT PostGIS_Version();")).scalar()
            assert version is not None and len(version) > 0
        finally:
            db.close()

    def test_complaints_table_has_ai_columns(self):
        db = SessionLocal()
        try:
            cols = {
                row[0]
                for row in db.execute(
                    text(
                        "SELECT column_name FROM information_schema.columns "
                        "WHERE table_name = 'complaints';"
                    )
                )
            }
            assert {"ai_category", "severity_score", "severity_level", "detections_count", "detection_details", "location"} <= cols
        finally:
            db.close()


# ---------------------------------------------------------------------------
# 4. AI severity engine wiring (Day 5)
# ---------------------------------------------------------------------------

class TestAIEngine:
    def test_severity_maths_critical_pothole(self):
        from ai_engine.severity import calculate_severity

        detection = {
            "class_id": 0,
            "class_name": "Pothole",
            "confidence": 0.91,
            "bbox": [100.0, 100.0, 420.0, 420.0],
            "bbox_normalized": [0.15, 0.15, 0.65, 0.65],  # area ratio 0.25
            "area_pixels": 102400.0,
        }
        result = calculate_severity([detection])
        # 0.25 * 100 * 1.0 * 3.4 = 85.0
        assert result["severity_score"] == 85.0
        assert result["severity_level"] == "CRITICAL"

    def test_severity_maths_no_detections_is_minor(self):
        from ai_engine.severity import calculate_severity

        result = calculate_severity([])
        assert result["severity_score"] == 0.0
        assert result["severity_level"] == "MINOR"

    def test_analyze_image_end_to_end(self, test_image_bytes):
        from app.services.ai_service import analyze_image

        result = analyze_image(test_image_bytes)
        assert set(result) == {
            "ai_category", "severity_score", "severity_level", "detections_count", "detection_details",
        }
        assert len(result["detection_details"]) == result["detections_count"]
        assert 0.0 <= result["severity_score"] <= 100.0
        assert result["severity_level"] in ("CRITICAL", "MODERATE", "MINOR")


# ---------------------------------------------------------------------------
# 5. Celery worker queue wiring (Day 6)
# ---------------------------------------------------------------------------

class TestCeleryWiring:
    def test_celery_configured_with_redis_broker(self):
        assert celery_app.conf.broker_url == settings.REDIS_URL
        assert "app.tasks.ai_tasks.process_complaint_ai_task" in celery_app.tasks

    def test_redis_broker_reachable(self):
        import redis as redis_lib

        r = redis_lib.Redis.from_url(settings.REDIS_URL, socket_connect_timeout=5)
        assert r.ping() is True


# ---------------------------------------------------------------------------
# 6. Full complaint lifecycle: POST 202 -> Celery task -> enriched row
# ---------------------------------------------------------------------------

class TestComplaintLifecycle:
    def test_full_async_complaint_flow(self, auth_client, test_image_bytes):
        created_id = None
        uploaded_image_url = None
        db = SessionLocal()
        try:
            # Step 1: submit complaint -> API must answer 202 with PROCESSING
            resp = auth_client.post(
                "/api/v1/complaints",
                data={
                    "latitude": "19.0760",
                    "longitude": "72.8777",
                    "category": "Pothole",
                    "description": "Integration test complaint (Day 7)",
                },
                files={"file": ("pothole.jpg", test_image_bytes, "image/jpeg")},
            )
            assert resp.status_code == 202, resp.text
            body = resp.json()
            created_id = body["id"]
            uploaded_image_url = body["image_url"]
            assert body["status"] == "PROCESSING"
            assert body["severity_level"] == "PENDING"
            assert body["detections_count"] == 0
            assert body["image_url"].startswith("http")

            # Step 2: raw row exists in Neon with a real PostGIS point
            row = db.query(Complaint).filter(Complaint.id == created_id).first()
            assert row is not None
            assert row.user_id == TEST_USER_ID
            coords = db.execute(
                text(
                    "SELECT ST_Y(location::geometry), ST_X(location::geometry) "
                    "FROM complaints WHERE id = :cid"
                ),
                {"cid": created_id},
            ).first()
            assert coords[0] == pytest.approx(19.0760, abs=1e-4)
            assert coords[1] == pytest.approx(72.8777, abs=1e-4)

            # Step 3: execute the worker task (locally, same code a worker runs)
            task_result = process_complaint_ai_task.apply(args=[created_id])
            assert task_result.successful()

            # Step 4: row must now be enriched and released from PROCESSING
            db.expire_all()
            row = db.query(Complaint).filter(Complaint.id == created_id).first()
            assert row.status == "RECEIVED"
            assert row.severity_level in ("CRITICAL", "MODERATE", "MINOR")
            assert 0.0 <= row.severity_score <= 100.0
            assert row.detections_count == task_result.result["detections_count"]
            assert len(row.detection_details) == row.detections_count
        finally:
            try:
                if created_id:
                    db.query(Complaint).filter(Complaint.id == created_id).delete()
                    db.commit()
            finally:
                db.close()
                if uploaded_image_url:
                    from app.services.storage import delete_file_from_supabase

                    delete_file_from_supabase(uploaded_image_url)

    def test_invalid_coordinates_rejected(self, auth_client, test_image_bytes):
        resp = auth_client.post(
            "/api/v1/complaints",
            data={"latitude": "999", "longitude": "72.87", "category": "Pothole"},
            files={"file": ("x.jpg", test_image_bytes, "image/jpeg")},
        )
        assert resp.status_code == 422

    def test_missing_complaint_task_is_dropped_gracefully(self):
        ghost_id = str(uuid.uuid4())
        result = process_complaint_ai_task.apply(args=[ghost_id])
        assert result.successful()
        assert result.result["status"] == "NOT_FOUND"
