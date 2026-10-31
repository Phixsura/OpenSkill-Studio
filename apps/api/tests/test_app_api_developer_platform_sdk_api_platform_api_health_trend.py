from app.services.app_api_developer_platform_sdk_api_platform_api_health_trend import AppAPIDeveloperPlatformSDKApiPlatformApiHealthTrend

class TestApiHealthTrend:
    def test_record(self):
        t = AppAPIDeveloperPlatformSDKApiPlatformApiHealthTrend()
        dp = t.record("inst-1", "2025-01-01", 99.99, 0.1, 45)
        assert dp.health_score == 100

    def test_degraded_score(self):
        t = AppAPIDeveloperPlatformSDKApiPlatformApiHealthTrend()
        dp = t.record("inst-1", "2025-01-01", 99.0, 5.0, 800, 2)
        assert dp.health_score <= 20

    def test_trend(self):
        t = AppAPIDeveloperPlatformSDKApiPlatformApiHealthTrend()
        t.record("inst-1", "2025-01-01", 99.99, 0.1, 45)
        t.record("inst-1", "2025-01-02", 99.95, 0.2, 50)
        assert len(t.trend("inst-1")) == 2

    def test_avg_score(self):
        t = AppAPIDeveloperPlatformSDKApiPlatformApiHealthTrend()
        t.record("inst-1", "2025-01-01", 99.99, 0.1, 45)
        t.record("inst-1", "2025-01-02", 99.99, 0.1, 45)
        assert t.avg_score("inst-1") == 100.0

    def test_isolation(self):
        t = AppAPIDeveloperPlatformSDKApiPlatformApiHealthTrend()
        t.record("inst-1", "2025-01-01", 99.99, 0.1, 45)
        assert t.latest_score("inst-2") == 100
