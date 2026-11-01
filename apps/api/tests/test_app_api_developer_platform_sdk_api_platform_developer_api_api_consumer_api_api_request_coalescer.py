from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_request_coalescer import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestCoalescer

class TestRequestCoalescer:
    def test_first_is_leader(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestCoalescer(window_ms=5000)
        req, is_leader = svc.coalesce("inst-1", "GET", "/users", "c1")
        assert is_leader is True

    def test_duplicate_coalesced(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestCoalescer(window_ms=5000)
        svc.coalesce("inst-1", "GET", "/users", "c1")
        req2, is_leader2 = svc.coalesce("inst-1", "GET", "/users", "c1")
        assert is_leader2 is False
        assert req2.waiting_count == 2

    def test_resolve(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestCoalescer(window_ms=5000)
        req, _ = svc.coalesce("inst-1", "GET", "/api", "c1")
        resolved = svc.resolve("inst-1", req.fingerprint, 200)
        assert resolved.resolved is True

    def test_coalesce_rate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestCoalescer(window_ms=5000)
        svc.coalesce("inst-1", "GET", "/a", "c1")
        svc.coalesce("inst-1", "GET", "/a", "c1")  # coalesced
        assert svc.coalesce_rate("inst-1") == 50.0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestCoalescer()
        svc.coalesce("inst-1", "GET", "/a", "c1")
        assert svc.pending_count("inst-2") == 0
