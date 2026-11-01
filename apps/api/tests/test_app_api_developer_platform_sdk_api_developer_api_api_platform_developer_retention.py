from app.services.app_api_developer_platform_sdk_api_developer_api_api_platform_developer_retention import AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformDeveloperRetention

class TestDeveloperRetention:
    def test_record(self):
        r = AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformDeveloperRetention()
        c = r.record("inst-1", "2025-01", 100, month_1=85, month_3=70, month_6=55, month_12=40)
        assert c.retention_1m == 85.0
        assert c.retention_3m == 70.0
        assert c.health == "excellent"

    def test_poor_retention(self):
        r = AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformDeveloperRetention()
        c = r.record("inst-1", "2025-01", 100, month_3=20)
        assert c.health == "poor"

    def test_avg_retention(self):
        r = AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformDeveloperRetention()
        r.record("inst-1", "2025-01", 100, month_3=70)
        r.record("inst-1", "2025-02", 100, month_3=80)
        assert r.avg_retention_3m("inst-1") == 75.0

    def test_isolation(self):
        r = AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformDeveloperRetention()
        r.record("inst-1", "2025-01", 100, month_3=70)
        assert r.avg_retention_3m("inst-2") == 0.0
