from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_error_classifier import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiErrorClassifier, classify_status,
)

class TestErrorClassifier:
    def test_classify_status_codes(self):
        assert classify_status(401) == "auth"
        assert classify_status(422) == "validation"
        assert classify_status(429) == "rate_limit"
        assert classify_status(500) == "server"
        assert classify_status(504) == "timeout"

    def test_classify_and_count(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiErrorClassifier()
        svc.classify("inst-1", "e1", 401, "Unauthorized")
        svc.classify("inst-1", "e2", 500, "Internal error")
        cats = svc.by_category("inst-1")
        assert cats["auth"] == 1 and cats["server"] == 1

    def test_top_errors(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiErrorClassifier()
        for i in range(5): svc.classify("inst-1", f"e{i}", 500, f"Error {i}")
        top = svc.top_errors("inst-1", 3)
        assert len(top) == 3

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiErrorClassifier()
        svc.classify("inst-1", "e1", 500, "err")
        assert svc.error_count("inst-2") == 0
