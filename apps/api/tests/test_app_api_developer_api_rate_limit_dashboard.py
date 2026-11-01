import time, pytest
from app.services.app_api_developer_api_rate_limit_dashboard import AppAPIDeveloperAPIRateLimitDashboard

class TestRateLimitDashboard:
    def test_record(self):
        d = AppAPIDeveloperAPIRateLimitDashboard()
        s = d.record("inst-1", "/api/users", 1000, 200, time.time() + 60)
        assert s.usage_pct == 80.0

    def test_hotspots(self):
        d = AppAPIDeveloperAPIRateLimitDashboard()
        d.record("inst-1", "/api/a", 100, 10, time.time() + 60)
        d.record("inst-1", "/api/b", 100, 80, time.time() + 60)
        assert len(d.hotspots("inst-1")) == 1

    def test_by_consumer(self):
        d = AppAPIDeveloperAPIRateLimitDashboard()
        d.record("inst-1", "/api/a", 100, 50, time.time() + 60, consumer_id="c1")
        d.record("inst-1", "/api/a", 100, 50, time.time() + 60, consumer_id="c2")
        assert len(d.by_consumer("inst-1", "c1")) == 1

    def test_isolation(self):
        d = AppAPIDeveloperAPIRateLimitDashboard()
        d.record("inst-1", "/api/a", 100, 50, time.time() + 60)
        assert len(d.hotspots("inst-2")) == 0
