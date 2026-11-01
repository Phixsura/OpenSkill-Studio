from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_key_analytics import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiKeyAnalytics

class TestApiKeyAnalytics:
    def test_record_and_usage(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiKeyAnalytics()
        svc.record("inst-1", "k1", "c1", "/users", True)
        svc.record("inst-1", "k1", "c1", "/orders", False)
        u = svc.get_usage("inst-1", "k1")
        assert u.total_requests == 2 and u.error_rate == 50.0
        assert len(u.unique_endpoints) == 2

    def test_top_keys(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiKeyAnalytics()
        for _ in range(10): svc.record("inst-1", "k1", "c1", "/a", True)
        for _ in range(5): svc.record("inst-1", "k2", "c1", "/a", True)
        top = svc.top_keys("inst-1", 1)
        assert top[0].key_id == "k1"

    def test_unknown_key(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiKeyAnalytics()
        assert svc.get_usage("inst-1", "nope") is None

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiKeyAnalytics()
        svc.record("inst-1", "k1", "c1", "/a", True)
        assert svc.key_count("inst-2") == 0
