from app.services.app_api_usage_breakdown import AppAPIUsageBreakdown

class TestBreakdown:
    def test_record(self):
        b = AppAPIUsageBreakdown()
        b.record("inst-1", "/api/users", "GET", "app-1")
        assert b.top_endpoints("inst-1")[0]["count"] == 1

    def test_top_endpoints(self):
        b = AppAPIUsageBreakdown()
        for _ in range(5): b.record("inst-1", "/api/users", "GET", "a")
        for _ in range(3): b.record("inst-1", "/api/apps", "GET", "a")
        top = b.top_endpoints("inst-1")
        assert top[0]["name"] == "/api/users"

    def test_method_breakdown(self):
        b = AppAPIUsageBreakdown()
        b.record("inst-1", "/a", "GET", "x")
        b.record("inst-1", "/a", "POST", "x")
        b.record("inst-1", "/a", "GET", "x")
        assert b.method_breakdown("inst-1") == {"GET": 2, "POST": 1}

    def test_isolation(self):
        b = AppAPIUsageBreakdown()
        b.record("inst-1", "/a", "GET", "x")
        assert b.top_endpoints("inst-2") == []
