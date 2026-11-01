from app.services.app_api_developer_api_key_analytics import AppAPIDeveloperAPIKeyAnalytics

class TestKeyAnalytics:
    def test_record(self):
        a = AppAPIDeveloperAPIKeyAnalytics()
        ka = a.record("inst-1", "k1", "/api/users", 50, True)
        assert ka.total_requests == 1

    def test_error_rate(self):
        a = AppAPIDeveloperAPIKeyAnalytics()
        for _ in range(8): a.record("inst-1", "k1", "/api", 50, True)
        for _ in range(2): a.record("inst-1", "k1", "/api", 100, False)
        assert a.get("inst-1", "k1").error_rate == 20.0

    def test_top_keys(self):
        a = AppAPIDeveloperAPIKeyAnalytics()
        for _ in range(10): a.record("inst-1", "k1", "/api", 50, True)
        for _ in range(5): a.record("inst-1", "k2", "/api", 50, True)
        assert a.top_keys("inst-1")[0].key_id == "k1"

    def test_isolation(self):
        a = AppAPIDeveloperAPIKeyAnalytics()
        a.record("inst-1", "k1", "/api", 50, True)
        assert a.top_keys("inst-2") == []
