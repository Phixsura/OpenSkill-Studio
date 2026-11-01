from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_request_payload_size_tracker import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestPayloadSizeTracker

class TestRequestPayloadSizeTracker:
    def test_record_and_stats(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestPayloadSizeTracker()
        svc.record("inst-1", "/users", "POST", 1024, 2048)
        svc.record("inst-1", "/users", "POST", 512, 4096)
        s = svc._stats[("inst-1", "POST", "/users")]
        assert s.request_count == 2
        assert s.avg_request_bytes == 768
        assert s.max_response_bytes == 4096

    def test_largest_payloads(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestPayloadSizeTracker()
        svc.record("inst-1", "/small", "GET", 100, 200)
        svc.record("inst-1", "/big", "POST", 50000, 100000)
        top = svc.largest_payloads("inst-1", 1)
        assert top[0].endpoint == "/big"

    def test_total_transfer(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestPayloadSizeTracker()
        svc.record("inst-1", "/api", "GET", 524288, 524288)  # 0.5MB each
        assert svc.total_transfer("inst-1") == 1.0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestPayloadSizeTracker()
        svc.record("inst-1", "/api", "GET", 100, 200)
        assert len(svc.list_stats("inst-2")) == 0
