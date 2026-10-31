from app.services.app_api_developer_platform_sdk_api_developer_api_api_platform_usage_breakdown import AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformUsageBreakdown

class TestPlatformUsageBreakdown:
    def test_record(self):
        b = AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformUsageBreakdown()
        r = b.record("inst-1", "2025-01", api_calls=100000, webhook_deliveries=50000)
        assert r.total_operations == 150000

    def test_cost_weighted(self):
        b = AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformUsageBreakdown()
        r = b.record("inst-1", "2025-01", api_calls=10000, webhook_deliveries=5000, storage_mb=100)
        assert r.cost_weighted_score > 0

    def test_trend(self):
        b = AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformUsageBreakdown()
        b.record("inst-1", "2025-02", api_calls=200000)
        b.record("inst-1", "2025-01", api_calls=100000)
        t = b.trend("inst-1")
        assert t[0].period == "2025-01"

    def test_total(self):
        b = AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformUsageBreakdown()
        b.record("inst-1", "2025-01", api_calls=100000, webhook_deliveries=50000)
        b.record("inst-1", "2025-02", api_calls=120000, webhook_deliveries=60000)
        assert b.total_operations("inst-1") == 330000

    def test_isolation(self):
        b = AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformUsageBreakdown()
        b.record("inst-1", "2025-01", api_calls=100000)
        assert b.total_operations("inst-2") == 0
