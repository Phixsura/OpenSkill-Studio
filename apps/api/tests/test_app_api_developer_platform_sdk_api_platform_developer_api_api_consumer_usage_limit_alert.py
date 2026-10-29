from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_usage_limit_alert import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerUsageLimitAlert

class TestConsumerUsageLimitAlert:
    def test_alert_at_threshold(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerUsageLimitAlert()
        alert = svc.check_and_alert("inst-1", "c1", "requests", 8000, 10000)
        assert alert is not None and alert.threshold_pct == 75

    def test_no_alert_below_threshold(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerUsageLimitAlert()
        alert = svc.check_and_alert("inst-1", "c1", "requests", 100, 10000)
        assert alert is None

    def test_no_duplicate_alert(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerUsageLimitAlert()
        svc.check_and_alert("inst-1", "c1", "requests", 8000, 10000)  # 80% → triggers 75
        alert = svc.check_and_alert("inst-1", "c1", "requests", 8100, 10000)  # still 81% → no new
        assert alert is None

    def test_acknowledge(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerUsageLimitAlert()
        alert = svc.check_and_alert("inst-1", "c1", "bandwidth", 9500, 10000)
        svc.acknowledge("inst-1", alert.alert_id)
        assert len(svc.unacknowledged("inst-1")) == 0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerUsageLimitAlert()
        svc.check_and_alert("inst-1", "c1", "requests", 9000, 10000)
        assert svc.alert_count("inst-2") == 0
