from app.services.app_api_developer_api_usage_trend import AppAPIDeveloperAPIUsageTrend

class TestTrend:
    def test_add(self):
        t = AppAPIDeveloperAPIUsageTrend()
        dp = t.add_point("inst-1", "2024-01", 10000, 100)
        assert dp.error_rate == 1.0

    def test_growth(self):
        t = AppAPIDeveloperAPIUsageTrend()
        t.add_point("inst-1", "2024-01", 10000, 100)
        t.add_point("inst-1", "2024-02", 12000, 120)
        assert t.growth_rate("inst-1") == 20.0

    def test_trend_limit(self):
        t = AppAPIDeveloperAPIUsageTrend()
        for i in range(20):
            t.add_point("inst-1", f"2024-{i:02d}", i * 1000, i * 10)
        assert len(t.trend("inst-1", 5)) == 5

    def test_isolation(self):
        t = AppAPIDeveloperAPIUsageTrend()
        t.add_point("inst-1", "2024-01", 1000, 10)
        assert t.trend("inst-2") == []
