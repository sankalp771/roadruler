"""
Phase 1 End-to-End Integration Test Suite
Validates citizen issue reporting flow: Auth headers, photo upload, PostGIS storage, and complaint lookup.
"""

import os
import sys
import io
import pytest

# Ensure backend directory is in sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from fastapi.testclient import TestClient
from PIL import Image

# Import FastAPI app from backend
from app.main import app
from app.api.deps import get_current_user

# Mock auth dependency for test client
app.dependency_overrides[get_current_user] = lambda: {"user_id": "test_user_123", "payload": {}}

client = TestClient(app)

def create_dummy_image():
    """Generates a simple 100x100 RGB image for testing file uploads."""
    img = Image.new('RGB', (100, 100), color='red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    return img_byte_arr

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to RoadRuler API"}

def test_phase1_e2e_complaint_lifecycle():
    """
    Day 7 E2E Integration Pass:
    1. Submit complaint POST /api/v1/complaints
    2. Verify HTTP status and returned payload
    3. Query GET /api/v1/complaints/{id} to verify persistence
    """
    dummy_img = create_dummy_image()
    
    payload = {
        "latitude": "19.2183",
        "longitude": "72.8731",
        "category": "POTHOLE",
        "description": "Integration test pothole on SV Road near Thakur College"
    }
    
    files = {
        "file": ("test_pothole.jpg", dummy_img, "image/jpeg")
    }

    headers = {
        "Authorization": "Bearer test_token"
    }

    # Step 1: Submit complaint
    response = client.post("/api/v1/complaints", data=payload, files=files, headers=headers)
    
    # Assert successful creation (HTTP 201) or valid response structure
    assert response.status_code in [200, 201], f"Expected 201 Created, got {response.status_code}: {response.text}"
    
    data = response.json()
    assert "id" in data, "Response must include complaint 'id'"
    assert "location" in data, "Response must include location object"
    assert data["location"]["lat"] == 19.2183
    assert data["location"]["lng"] == 72.8731
    
    complaint_id = data["id"]
    
    # Step 2: Query GET /api/v1/complaints/{id}
    get_response = client.get(f"/api/v1/complaints/{complaint_id}")
    assert get_response.status_code == 200, f"Expected 200 OK for GET complaint, got {get_response.status_code}"
    
    get_data = get_response.json()
    assert get_data["id"] == complaint_id
    assert get_data["category"] == "POTHOLE"
    assert get_data["status"] in ["RECEIVED", "SUBMITTED", "PENDING", "ANALYZED", "ASSIGNED", "IN_REPAIR", "RESOLVED"]
    assert "location" in get_data
    assert get_data["location"]["lat"] == 19.2183
    assert get_data["location"]["lng"] == 72.8731

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
