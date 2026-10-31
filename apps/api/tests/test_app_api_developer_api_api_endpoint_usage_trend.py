from app.services.app_api_developer_api_api_endpoint_usage_trend import AppAPIDeveloperAPIApiEndpointUsageTrend

class TestEndpointUsageTrend:
    def test_record(self):
        t = AppAPIDeveloperAPIApiEndpointUsageTrend()
        r = t.record("inst-1", "/api/users", "2025-01-01", 100)
        assert r.total == 100

    def test_growing(self):
        t = AppAPIDeveloperAPIApiEndpointUsageTrend()
        for i, count in enumerate([100, 110, 120, 200, 250, 300]):
            t.record("inst-1", "/api/users", f"2025-01-0{i+1}", count)
        trend = t.get_trend("inst-1", "/api/users")
        assert trend.trend_direction == "growing"

    def test_declining(self):
        t = AppAPIDeveloperAPIApiEndpointUsageTrend()
        for i, count in enumerate([300, 280, 260, 100, 80, 60]):
            t.record("inst-1", "/api/old", f"2025-01-0{i+1}", count)
        assert t.get_trend("inst-1", "/api/old").trend_direction == "declining"

    def test_avg_daily(self):
        t = AppAPIDeveloperAPIApiEndpointUsageTrend()
        t.record("inst-1", "/api", "2025-01-01", 100)
        t.record("inst-1", "/api", "2025-01-02", 200)
        assert t.get_trend("inst-1", "/api").avg_daily == 150.0

    def test_isolation(self):
        t = AppAPIDeveloperAPIApiEndpointUsageTrend()
        t.record("inst-1", "/api", "2025-01-01", 100)
        assert len(t.all_trends("inst-2")) == 0
