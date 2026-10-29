import time
from app.services.app_api_developer_api_api_rate_limit_override import AppAPIDeveloperAPIApiRateLimitOverride

class TestRateLimitOverride:
    def test_create(self):
        o = AppAPIDeveloperAPIApiRateLimitOverride()
        r = o.create("inst-1", "o1", "c1", "/api/users", 1000, "VIP customer")
        assert r.limit_per_minute == 1000

    def test_effective_limit(self):
        o = AppAPIDeveloperAPIApiRateLimitOverride()
        o.create("inst-1", "o1", "c1", "/api/users", 1000, "VIP")
        assert o.effective_limit("inst-1", "c1", "/api/users", 100) == 1000
        assert o.effective_limit("inst-1", "c2", "/api/users", 100) == 100

    def test_wildcard(self):
        o = AppAPIDeveloperAPIApiRateLimitOverride()
        o.create("inst-1", "o1", "c1", "*", 5000, "Enterprise")
        assert o.effective_limit("inst-1", "c1", "/any/endpoint", 100) == 5000

    def test_expired(self):
        o = AppAPIDeveloperAPIApiRateLimitOverride()
        o.create("inst-1", "o1", "c1", "*", 5000, "Temp", expires_at=time.time() - 10)
        assert o.effective_limit("inst-1", "c1", "/api", 100) == 100
        assert len(o.active("inst-1")) == 0

    def test_revoke(self):
        o = AppAPIDeveloperAPIApiRateLimitOverride()
        o.create("inst-1", "o1", "c1", "*", 5000, "test")
        o.revoke("inst-1", "o1")
        assert len(o.active("inst-1")) == 0

    def test_isolation(self):
        o = AppAPIDeveloperAPIApiRateLimitOverride()
        o.create("inst-1", "o1", "c1", "*", 1000, "test")
        assert len(o.active("inst-2")) == 0
