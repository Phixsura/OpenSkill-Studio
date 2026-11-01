from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_request_fingerprint import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestFingerprint

class TestRequestFingerprint:
    def test_same_request_increments(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestFingerprint()
        fp1 = svc.fingerprint("inst-1", "GET", "/users", "c1")
        fp2 = svc.fingerprint("inst-1", "GET", "/users", "c1")
        assert fp1.fingerprint_id == fp2.fingerprint_id
        assert fp2.hit_count == 2

    def test_different_requests(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestFingerprint()
        svc.fingerprint("inst-1", "GET", "/users", "c1")
        svc.fingerprint("inst-1", "POST", "/orders", "c1")
        assert svc.unique_count("inst-1") == 2

    def test_top_fingerprints(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestFingerprint()
        for _ in range(10): svc.fingerprint("inst-1", "GET", "/hot", "c1")
        for _ in range(3): svc.fingerprint("inst-1", "GET", "/cold", "c1")
        top = svc.top_fingerprints("inst-1", 1)
        assert top[0].path == "/hot"

    def test_dedup_ratio(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestFingerprint()
        svc.fingerprint("inst-1", "GET", "/a", "c1")
        svc.fingerprint("inst-1", "GET", "/a", "c1")  # dup
        assert svc.dedup_ratio("inst-1") == 50.0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestFingerprint()
        svc.fingerprint("inst-1", "GET", "/a", "c1")
        assert svc.unique_count("inst-2") == 0
