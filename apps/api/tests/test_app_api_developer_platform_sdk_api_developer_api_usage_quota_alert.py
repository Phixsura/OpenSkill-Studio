from app.services.app_api_developer_platform_sdk_api_developer_api_usage_quota_alert import AppAPIDeveloperPlatformSDKApiDeveloperApiUsageQuotaAlert

class TestUsageQuotaAlert:
    def test_configure(self):
        a = AppAPIDeveloperPlatformSDKApiDeveloperApiUsageQuotaAlert()
        al = a.configure("inst-1", "a1", "c1", "api_calls", 80.0)
        assert al.triggered is False

    def test_trigger(self):
        a = AppAPIDeveloperPlatformSDKApiDeveloperApiUsageQuotaAlert()
        a.configure("inst-1", "a1", "c1", "api_calls", 80.0)
        al = a.evaluate("inst-1", "a1", 90.0)
        assert al.triggered is True
        assert al.triggered_at is not None

    def test_no_trigger(self):
        a = AppAPIDeveloperPlatformSDKApiDeveloperApiUsageQuotaAlert()
        a.configure("inst-1", "a1", "c1", "api_calls", 80.0)
        al = a.evaluate("inst-1", "a1", 50.0)
        assert al.triggered is False

    def test_triggered_list(self):
        a = AppAPIDeveloperPlatformSDKApiDeveloperApiUsageQuotaAlert()
        a.configure("inst-1", "a1", "c1", "api_calls", 80.0)
        a.configure("inst-1", "a2", "c2", "storage", 90.0)
        a.evaluate("inst-1", "a1", 85.0)
        a.evaluate("inst-1", "a2", 50.0)
        assert len(a.triggered_alerts("inst-1")) == 1

    def test_isolation(self):
        a = AppAPIDeveloperPlatformSDKApiDeveloperApiUsageQuotaAlert()
        a.configure("inst-1", "a1", "c1", "api_calls", 80.0)
        assert len(a.all_alerts("inst-2")) == 0
