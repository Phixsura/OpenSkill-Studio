import pytest
from app.services.app_api_developer_api_api_resource_usage_limiter import AppAPIDeveloperAPIApiResourceUsageLimiter

class TestResourceUsageLimiter:
    def test_set_and_consume(self):
        l = AppAPIDeveloperAPIApiResourceUsageLimiter()
        l.set_limit("inst-1", "c1", "compute", 100.0, "cpu-hours")
        r = l.consume("inst-1", "c1", "compute", 30.0)
        assert r.remaining == 70.0
        assert r.usage_pct == 30.0

    def test_exceeded(self):
        l = AppAPIDeveloperAPIApiResourceUsageLimiter()
        l.set_limit("inst-1", "c1", "storage", 10.0, "GB")
        l.consume("inst-1", "c1", "storage", 10.0)
        with pytest.raises(ValueError, match="exceeded"):
            l.consume("inst-1", "c1", "storage", 1.0)

    def test_exceeded_list(self):
        l = AppAPIDeveloperAPIApiResourceUsageLimiter()
        l.set_limit("inst-1", "c1", "compute", 10.0)
        l.set_limit("inst-1", "c1", "storage", 100.0)
        l.consume("inst-1", "c1", "compute", 10.0)
        assert len(l.exceeded_limits("inst-1")) == 1

    def test_consumer_limits(self):
        l = AppAPIDeveloperAPIApiResourceUsageLimiter()
        l.set_limit("inst-1", "c1", "compute", 100.0)
        l.set_limit("inst-1", "c1", "storage", 50.0)
        assert len(l.consumer_limits("inst-1", "c1")) == 2

    def test_isolation(self):
        l = AppAPIDeveloperAPIApiResourceUsageLimiter()
        l.set_limit("inst-1", "c1", "compute", 100.0)
        assert len(l.exceeded_limits("inst-2")) == 0
