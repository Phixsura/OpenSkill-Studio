from app.services.app_api_developer_platform_sdk_api_developer_api_webhook_retry_analytics import AppAPIDeveloperPlatformSDKApiDeveloperApiWebhookRetryAnalytics

class TestRetryAnalytics:
    def test_record(self):
        a = AppAPIDeveloperPlatformSDKApiDeveloperApiWebhookRetryAnalytics()
        r = a.record("inst-1", "https://a.com", 3, True)
        assert r.total_retries == 3
        assert r.retry_success_rate == 100.0

    def test_exhausted(self):
        a = AppAPIDeveloperPlatformSDKApiDeveloperApiWebhookRetryAnalytics()
        a.record("inst-1", "https://a.com", 5, False, exhausted=True)
        r = a.all_analytics("inst-1")[0]
        assert r.exhausted_retries == 1

    def test_high_waste(self):
        a = AppAPIDeveloperPlatformSDKApiDeveloperApiWebhookRetryAnalytics()
        for _ in range(5): a.record("inst-1", "https://bad.com", 3, False, exhausted=True)
        assert len(a.high_waste("inst-1", 20)) == 1

    def test_total(self):
        a = AppAPIDeveloperPlatformSDKApiDeveloperApiWebhookRetryAnalytics()
        a.record("inst-1", "https://a.com", 3, True)
        a.record("inst-1", "https://b.com", 5, False)
        assert a.total_retries("inst-1") == 8

    def test_isolation(self):
        a = AppAPIDeveloperPlatformSDKApiDeveloperApiWebhookRetryAnalytics()
        a.record("inst-1", "https://a.com", 3, True)
        assert a.total_retries("inst-2") == 0
