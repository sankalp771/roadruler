"""
Shared pytest fixtures for backend integration tests (Day 7).
Tests run against the real Neon PostGIS database and real services;
only Clerk authentication is dependency-overridden (tests cannot mint
real Clerk JWTs non-interactively).
"""

import io
import sys
from pathlib import Path

import pytest

# Make `app` importable no matter where pytest is invoked from.
BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.api.deps import get_current_user  # noqa: E402

TEST_USER_ID = "user_integration_test_phase1"


@pytest.fixture()
def client():
    """Plain TestClient with real auth enforcement (for auth tests)."""
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def auth_client():
    """TestClient with Clerk auth overridden to a fixed test user."""
    app.dependency_overrides[get_current_user] = lambda: {
        "user_id": TEST_USER_ID,
        "payload": {"sub": TEST_USER_ID},
    }
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture()
def authority_client():
    """TestClient authenticated as a Clerk-verified ward officer."""
    app.dependency_overrides[get_current_user] = lambda: {
        "user_id": "user_integration_authority",
        "payload": {
            "sub": "user_integration_authority",
            "public_metadata": {"role": "WARD_OFFICER"},
        },
    }
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture()
def test_image_bytes() -> bytes:
    """Generate a real in-memory JPEG (dark asphalt-like patch)."""
    from PIL import Image

    img = Image.new("RGB", (640, 640), color=(72, 70, 68))
    # Draw a large dark blob so the image is not a uniform block
    for x in range(200, 440):
        for y in range(250, 420):
            img.putpixel((x, y), (28, 26, 25))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()
