from app.services.app_api_developer_api_api_developer_api_api_developer_api_api_api_developer_api_token_usage_monitor import AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiTokenUsageMonitor

class TestTokenUsageMonitor:
    def test_track(self):
        m = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiTokenUsageMonitor()
        u = m.track("inst-1", "sk-prod-ab", "c1", "/api/users")
        assert u.requests_total == 1

    def test_endpoints_tracked(self):
        m = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiTokenUsageMonitor()
        m.track("inst-1", "sk-a", "c1", "/api/users")
        m.track("inst-1", "sk-a", "c1", "/api/orders")
        u = m.get("inst-1", "sk-a")
        assert len(u.endpoints_accessed) == 2

    def test_error_rate(self):
        m = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiTokenUsageMonitor()
        for _ in range(9): m.track("inst-1", "sk-a", "c1", "/api", True)
        m.track("inst-1", "sk-a", "c1", "/api", False)
        assert m.get("inst-1", "sk-a").error_rate == 10.0

    def test_most_active(self):
        m = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiTokenUsageMonitor()
        for _ in range(10): m.track("inst-1", "sk-a", "c1", "/api")
        for _ in range(5): m.track("inst-1", "sk-b", "c2", "/api")
        assert m.most_active("inst-1", 1)[0].token_prefix == "sk-a"

    def test_isolation(self):
        m = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiTokenUsageMonitor()
        m.track("inst-1", "sk-a", "c1", "/api")
        assert len(m.all_tokens("inst-2")) == 0
