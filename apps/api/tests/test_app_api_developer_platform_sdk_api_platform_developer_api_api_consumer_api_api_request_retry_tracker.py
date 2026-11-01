from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_request_retry_tracker import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestRetryTracker

class TestRequestRetryTracker:
    def test_record_and_rate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestRetryTracker()
        svc.record_retry("inst-1", "c1", "/api", True)
        svc.record_retry("inst-1", "c1", "/api", False)
        r = svc.get_record("inst-1", "c1", "/api")
        assert r.retry_success_rate == 50.0

    def test_high_retry_endpoints(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestRetryTracker()
        for _ in range(15): svc.record_retry("inst-1", "c1", "/flaky", False)
        assert len(svc.high_retry_endpoints("inst-1", 10)) == 1

    def test_max_reached(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestRetryTracker()
        svc.record_retry("inst-1", "c1", "/api", False, max_reached=True)
        r = svc.get_record("inst-1", "c1", "/api")
        assert r.max_attempts_reached == 1

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestRetryTracker()
        svc.record_retry("inst-1", "c1", "/api", True)
        assert svc.total_retries("inst-2") == 0
