from app.services.app_api_developer_platform_sdk_api_developer_api_api_platform_growth_tracker import AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformGrowthTracker

class TestPlatformGrowthTracker:
    def test_record(self):
        g = AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformGrowthTracker()
        s = g.record("inst-1", "2025-01", total_consumers=100, new_consumers=20, churned_consumers=5, mrr_cents=500000)
        assert s.net_growth == 15
        assert s.growth_healthy is True

    def test_unhealthy_churn(self):
        g = AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformGrowthTracker()
        s = g.record("inst-1", "2025-01", total_consumers=100, new_consumers=3, churned_consumers=10)
        assert s.growth_healthy is False

    def test_trend(self):
        g = AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformGrowthTracker()
        g.record("inst-1", "2025-02", total_consumers=120)
        g.record("inst-1", "2025-01", total_consumers=100)
        t = g.trend("inst-1")
        assert t[0].period == "2025-01"

    def test_latest(self):
        g = AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformGrowthTracker()
        g.record("inst-1", "2025-01", mrr_cents=100000)
        g.record("inst-1", "2025-02", mrr_cents=120000)
        assert g.total_mrr("inst-1") == 120000

    def test_isolation(self):
        g = AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformGrowthTracker()
        g.record("inst-1", "2025-01", mrr_cents=100000)
        assert g.total_mrr("inst-2") == 0
