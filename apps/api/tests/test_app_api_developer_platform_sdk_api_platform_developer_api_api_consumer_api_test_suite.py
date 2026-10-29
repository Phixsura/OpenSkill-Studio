from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_test_suite import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiTestSuite, TestRun, TestCase, RunStatus,
)

class TestConsumerApiTestSuite:
    def test_create_and_run(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiTestSuite()
        tests = [TestCase(test_id="t1", name="Get users", endpoint="/users", method="GET", expected_status=200)]
        svc.create_run("inst-1", TestRun(run_id="r1", consumer_id="c1", tests=tests))
        svc.start_run("inst-1", "r1")
        svc.record_result("inst-1", "r1", "t1", 200)
        run = svc.get_run("inst-1", "r1")
        assert run.status == RunStatus.PASSED
        assert run.pass_count == 1

    def test_failed_run(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiTestSuite()
        tests = [TestCase(test_id="t1", name="Test", endpoint="/a", method="GET", expected_status=200)]
        svc.create_run("inst-1", TestRun(run_id="r1", consumer_id="c1", tests=tests))
        svc.record_result("inst-1", "r1", "t1", 500)
        assert svc.get_run("inst-1", "r1").status == RunStatus.FAILED

    def test_pass_rate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiTestSuite()
        tests = [TestCase(test_id="t1", name="A", endpoint="/a", method="GET", expected_status=200), TestCase(test_id="t2", name="B", endpoint="/b", method="GET", expected_status=200)]
        svc.create_run("inst-1", TestRun(run_id="r1", consumer_id="c1", tests=tests))
        svc.record_result("inst-1", "r1", "t1", 200)
        svc.record_result("inst-1", "r1", "t2", 500)
        assert svc.pass_rate("inst-1", "r1") == 50.0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiTestSuite()
        svc.create_run("inst-1", TestRun(run_id="r1", consumer_id="c1", tests=[TestCase(test_id="t1", name="X", endpoint="/x", method="GET", expected_status=200)]))
        assert len(svc.list_runs("inst-2")) == 0
