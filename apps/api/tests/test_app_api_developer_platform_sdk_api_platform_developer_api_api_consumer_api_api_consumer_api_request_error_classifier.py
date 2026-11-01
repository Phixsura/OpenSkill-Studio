from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_request_error_classifier import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestErrorClassifier, classify,
)

class TestRequestErrorClassifier:
    def test_classify_codes(self):
        assert classify(401) == "auth_failure"
        assert classify(422) == "validation"
        assert classify(429) == "rate_limited"
        assert classify(500) == "server_error"
        assert classify(504) == "timeout"

    def test_record_and_by_cause(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestErrorClassifier()
        svc.record("inst-1", "e1", 401, "/api", "c1")
        svc.record("inst-1", "e2", 500, "/api", "c1")
        causes = svc.by_root_cause("inst-1")
        assert causes["auth_failure"] == 1 and causes["server_error"] == 1

    def test_top_error_endpoints(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestErrorClassifier()
        for _ in range(10): svc.record("inst-1", "e", 500, "/bad", "c1")
        for _ in range(3): svc.record("inst-1", "e", 500, "/ok", "c1")
        top = svc.top_error_endpoints("inst-1", 1)
        assert top[0][0] == "/bad"

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestErrorClassifier()
        svc.record("inst-1", "e1", 500, "/api", "c1")
        assert svc.error_count("inst-2") == 0
