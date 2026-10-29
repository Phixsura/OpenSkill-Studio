import time
from app.services.app_api_developer_api_api_key_analytics import AppAPIDeveloperAPIApiKeyAnalytics

class TestApiKeyAnalytics:
    def test_track(self):
        a = AppAPIDeveloperAPIApiKeyAnalytics()
        u = a.track("inst-1", "k1", "sk-abcd12", "/api/users", True)
        assert u.total_requests == 1
        assert u.key_prefix == "sk-abcd1"  # truncated to 8... wait it's 8 already

    def test_top_keys(self):
        a = AppAPIDeveloperAPIApiKeyAnalytics()
        for _ in range(10): a.track("inst-1", "k1", "sk-a", "/api/a", True)
        for _ in range(5): a.track("inst-1", "k2", "sk-b", "/api/b", True)
        top = a.top_keys("inst-1")
        assert top[0].key_id == "k1"

    def test_error_tracking(self):
        a = AppAPIDeveloperAPIApiKeyAnalytics()
        a.track("inst-1", "k1", "sk-a", "/api/a", False)
        assert a.get("inst-1", "k1").error_count == 1

    def test_isolation(self):
        a = AppAPIDeveloperAPIApiKeyAnalytics()
        a.track("inst-1", "k1", "sk-a", "/api/a", True)
        assert len(a.top_keys("inst-2")) == 0
