import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_integration_test_runner import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiIntegrationTestRunner, TestCase,
)

class TestConsumerApiIntegrationTestRunner:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_register_and_run(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiIntegrationTestRunner()
        cases = [TestCase(test_id="t1", name="List Users", method="GET", path="/api/users", expected_status=200)]
        svc.register_suite("inst-1", "c1", "basic", cases)
        run = svc.run_suite("inst-1", "c1", "basic", self._now())
        assert run.passed == 1 and run.failed == 0

    def test_multiple_cases(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiIntegrationTestRunner()
        cases = [
            TestCase(test_id="t1", name="A", method="GET", path="/a", expected_status=200),
            TestCase(test_id="t2", name="B", method="POST", path="/b", expected_status=201),
        ]
        svc.register_suite("inst-1", "c1", "full", cases)
        run = svc.run_suite("inst-1", "c1", "full", self._now())
        assert run.passed == 2 and len(run.results) == 2

    def test_run_history(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiIntegrationTestRunner()
        svc.register_suite("inst-1", "c1", "s", [TestCase(test_id="t1", name="T", method="GET", path="/", expected_status=200)])
        svc.run_suite("inst-1", "c1", "s", self._now())
        svc.run_suite("inst-1", "c1", "s", self._now())
        assert len(svc.get_runs("inst-1", "c1")) == 2

    def test_empty_suite_rejected(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiIntegrationTestRunner()
        with pytest.raises(ValueError, match="At least one"):
            svc.register_suite("inst-1", "c1", "empty", [])

    def test_suite_not_found(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiIntegrationTestRunner()
        with pytest.raises(ValueError, match="Suite not found"):
            svc.run_suite("inst-1", "c1", "missing", self._now())

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiIntegrationTestRunner()
        svc.register_suite("inst-1", "c1", "s", [TestCase(test_id="t1", name="T", method="GET", path="/", expected_status=200)])
        assert len(svc.list_suites("inst-2", "c1")) == 0
