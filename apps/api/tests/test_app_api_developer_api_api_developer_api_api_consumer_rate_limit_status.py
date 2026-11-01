import time
from app.services.app_api_developer_api_api_developer_api_api_consumer_rate_limit_status import AppAPIDeveloperAPIApiDeveloperApiApiConsumerRateLimitStatus

class TestConsumerRateLimitStatus:
    def test_update(self):
        s = AppAPIDeveloperAPIApiDeveloperApiApiConsumerRateLimitStatus()
        r = s.update("inst-1", "c1", "/api/users", 1000, 800, time.time() + 60)
        assert r.usage_pct == 20.0
        assert r.throttled is False

    def test_throttled(self):
        s = AppAPIDeveloperAPIApiDeveloperApiApiConsumerRateLimitStatus()
        r = s.update("inst-1", "c1", "/api", 100, 0, time.time() + 30)
        assert r.throttled is True

    def test_throttled_list(self):
        s = AppAPIDeveloperAPIApiDeveloperApiApiConsumerRateLimitStatus()
        s.update("inst-1", "c1", "/api", 100, 0, time.time() + 60)
        s.update("inst-1", "c2", "/api", 100, 50, time.time() + 60)
        assert len(s.throttled_consumers("inst-1")) == 1

    def test_near_limit(self):
        s = AppAPIDeveloperAPIApiDeveloperApiApiConsumerRateLimitStatus()
        s.update("inst-1", "c1", "/api", 100, 15, time.time() + 60)
        s.update("inst-1", "c2", "/api", 100, 80, time.time() + 60)
        assert len(s.near_limit("inst-1", 80)) == 1

    def test_isolation(self):
        s = AppAPIDeveloperAPIApiDeveloperApiApiConsumerRateLimitStatus()
        s.update("inst-1", "c1", "/api", 100, 50, time.time() + 60)
        assert len(s.throttled_consumers("inst-2")) == 0
