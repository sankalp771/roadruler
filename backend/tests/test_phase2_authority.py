from fastapi.testclient import TestClient

from app.api.deps import get_current_user
from app.main import app


def test_authority_endpoints_reject_citizen_role():
    app.dependency_overrides[get_current_user] = lambda: {
        "user_id": "citizen_test",
        "payload": {"sub": "citizen_test", "public_metadata": {"role": "CITIZEN"}},
    }
    try:
        with TestClient(app) as client:
            assert client.get("/api/v1/authority/complaints").status_code == 403
            assert client.get("/api/v1/analytics/hotspots").status_code == 403
    finally:
        app.dependency_overrides.pop(get_current_user, None)


def test_authority_endpoints_reject_token_without_role():
    app.dependency_overrides[get_current_user] = lambda: {
        "user_id": "roleless_test",
        "payload": {"sub": "roleless_test"},
    }
    try:
        with TestClient(app) as client:
            assert client.get("/api/v1/authority/complaints").status_code == 403
            assert client.get("/api/v1/analytics/hotspots").status_code == 403
    finally:
        app.dependency_overrides.pop(get_current_user, None)


def test_officer_can_read_paginated_queue_and_geojson_hotspots():
    app.dependency_overrides[get_current_user] = lambda: {
        "user_id": "ward_officer_test",
        "payload": {"sub": "ward_officer_test", "public_metadata": {"role": "WARD_OFFICER"}},
    }
    try:
        with TestClient(app) as client:
            queue = client.get("/api/v1/authority/complaints?page=1&limit=1")
            filtered_queue = client.get(
                "/api/v1/authority/complaints?ward_id=WARD_WITH_NO_MATCH&severity=CRITICAL&status=RECEIVED"
            )
            hotspots = client.get("/api/v1/analytics/hotspots")
        assert queue.status_code == 200, queue.text
        page = queue.json()
        assert {"items", "total", "page", "limit", "pages"}.issubset(page)
        assert len(page["items"]) <= 1
        assert filtered_queue.status_code == 200, filtered_queue.text
        assert filtered_queue.json()["total"] == 0
        assert hotspots.status_code == 200, hotspots.text
        collection = hotspots.json()
        assert collection["type"] == "FeatureCollection"
        assert isinstance(collection["features"], list)
        for feature in collection["features"]:
            assert feature["geometry"]["type"] == "Point"
            assert len(feature["geometry"]["coordinates"]) == 2
            assert {"cluster_id", "complaint_count", "avg_severity", "dominant_category", "risk_level"}.issubset(feature["properties"])
    finally:
        app.dependency_overrides.pop(get_current_user, None)
