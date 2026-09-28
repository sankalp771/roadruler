import json
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.api.routes import public
from app.main import app


def test_public_stats_endpoint_is_anonymous_and_uses_five_minute_cache(monkeypatch):
    class FakeRedis:
        value = None
        writes = []

        def get(self, key):
            assert key == public.CACHE_KEY
            return self.value

        def set(self, key, value, ex):
            self.writes.append((key, json.loads(value), ex))
            self.value = value

        def close(self):
            pass

    fake_redis = FakeRedis()
    computed = []
    result = public.PublicStats(
        generated_at=datetime(2026, 9, 29, tzinfo=timezone.utc),
        total_complaints=4,
        resolved_complaints=2,
        resolution_rate=50.0,
        average_resolution_days=3.0,
        wards=[],
    )
    monkeypatch.setattr(public, "get_redis_client", lambda: fake_redis)
    monkeypatch.setattr(public, "build_public_stats", lambda _db: (computed.append(True), result)[1])

    with TestClient(app) as client:
        first = client.get("/api/v1/public/stats")
        second = client.get("/api/v1/public/stats")

    assert first.status_code == second.status_code == 200
    assert first.json()["resolution_rate"] == 50.0
    assert second.json() == first.json()
    assert computed == [True]
    assert len(fake_redis.writes) == 1
    assert fake_redis.writes[0][2] == 300
