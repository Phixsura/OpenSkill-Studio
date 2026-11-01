from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_response_validator import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiResponseValidator, ResponseExpectation,
)

class TestResponseValidator:
    def test_pass(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiResponseValidator()
        svc.set_expectation("inst-1", "c1", ResponseExpectation(endpoint="/users", method="GET", expected_status=200, required_fields=["id", "name"]))
        r = svc.validate("inst-1", "c1", "GET", "/users", 200, "application/json", ["id", "name", "email"])
        assert r.passed is True

    def test_fail_status(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiResponseValidator()
        svc.set_expectation("inst-1", "c1", ResponseExpectation(endpoint="/users", method="GET", expected_status=200))
        r = svc.validate("inst-1", "c1", "GET", "/users", 500)
        assert r.passed is False and "Status" in r.failures[0]

    def test_fail_missing_fields(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiResponseValidator()
        svc.set_expectation("inst-1", "c1", ResponseExpectation(endpoint="/a", method="GET", expected_status=200, required_fields=["id", "name"]))
        r = svc.validate("inst-1", "c1", "GET", "/a", 200, actual_fields=["id"])
        assert r.passed is False

    def test_fail_latency(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiResponseValidator()
        svc.set_expectation("inst-1", "c1", ResponseExpectation(endpoint="/a", method="GET", expected_status=200, max_latency_ms=100))
        r = svc.validate("inst-1", "c1", "GET", "/a", 200, latency_ms=500)
        assert r.passed is False

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiResponseValidator()
        svc.set_expectation("inst-1", "c1", ResponseExpectation(endpoint="/a", method="GET", expected_status=200))
        assert len(svc.list_expectations("inst-2", "c1")) == 0
