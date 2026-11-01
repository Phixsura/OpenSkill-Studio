from app.services.app_api_developer_platform_sdk_api_developer_api_rate_limit_analytics import AppAPIDeveloperPlatformSDKApiDeveloperApiRateLimitAnalytics

class TestRateLimitAnalytics:
    def test_record(self):
        a = AppAPIDeveloperPlatformSDKApiDeveloperApiRateLimitAnalytics()
        r = a.record("inst-1", "c1", 10000, 500, 200, 100)
        assert r.throttle_rate == 5.0
        assert r.needs_upgrade is True

    def test_no_upgrade(self):
        a = AppAPIDeveloperPlatformSDKApiDeveloperApiRateLimitAnalytics()
        r = a.record("inst-1", "c1", 10000, 100, 50, 30)
        assert r.needs_upgrade is False

    def test_most_throttled(self):
        a = AppAPIDeveloperPlatformSDKApiDeveloperApiRateLimitAnalytics()
        a.record("inst-1", "c1", 1000, 100, 50, 30)
        a.record("inst-1", "c2", 1000, 500, 80, 60)
        top = a.most_throttled("inst-1", 1)
        assert top[0].consumer_id == "c2"

    def test_isolation(self):
        a = AppAPIDeveloperPlatformSDKApiDeveloperApiRateLimitAnalytics()
        a.record("inst-1", "c1", 1000, 50, 50, 30)
        assert len(a.all_analytics("inst-2")) == 0
