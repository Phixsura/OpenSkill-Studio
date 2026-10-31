from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_request_deduplicator import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiRequestDeduplicator

class TestRequestDeduplicator:
    def test_first_request_not_duplicate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiRequestDeduplicator(window_s=10)
        result = svc.check("inst-1", "POST", "/orders", '{"item":"a"}', "c1")
        assert result["duplicate"] is False

    def test_duplicate_detected(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiRequestDeduplicator(window_s=10)
        svc.check("inst-1", "POST", "/orders", '{"item":"a"}', "c1")
        result = svc.check("inst-1", "POST", "/orders", '{"item":"a"}', "c1")
        assert result["duplicate"] is True
        assert result["count"] == 2

    def test_different_body_not_duplicate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiRequestDeduplicator(window_s=10)
        svc.check("inst-1", "POST", "/orders", '{"item":"a"}', "c1")
        result = svc.check("inst-1", "POST", "/orders", '{"item":"b"}', "c1")
        assert result["duplicate"] is False

    def test_stats(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiRequestDeduplicator(window_s=10)
        svc.check("inst-1", "POST", "/a", "{}", "c1")
        svc.check("inst-1", "POST", "/a", "{}", "c1")  # dupe
        svc.check("inst-1", "POST", "/b", "{}", "c1")
        s = svc.stats("inst-1")
        assert s["duplicates_detected"] == 1

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiRequestDeduplicator(window_s=10)
        svc.check("inst-1", "POST", "/a", "{}", "c1")
        assert svc.stats("inst-2")["total_fingerprints"] == 0
