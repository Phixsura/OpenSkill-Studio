from app.services.app_api_developer_platform_sdk_api_platform_developer_api_consumer_contract_test import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerContractTest, ContractTest, TestResult,
)

class TestConsumerContractTest:
    def test_pass(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerContractTest()
        svc.add_test("inst-1", ContractTest(test_id="t1", consumer_id="c1", endpoint="/users", method="GET", expected_status=200, expected_fields=["id", "name"]))
        ex = svc.execute("inst-1", "t1", "c1", 200, ["id", "name", "email"])
        assert ex.result == TestResult.PASSED

    def test_fail_status(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerContractTest()
        svc.add_test("inst-1", ContractTest(test_id="t1", consumer_id="c1", endpoint="/users", method="GET", expected_status=200))
        ex = svc.execute("inst-1", "t1", "c1", 500, [])
        assert ex.result == TestResult.FAILED

    def test_fail_missing_fields(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerContractTest()
        svc.add_test("inst-1", ContractTest(test_id="t1", consumer_id="c1", endpoint="/users", method="GET", expected_status=200, expected_fields=["id", "name"]))
        ex = svc.execute("inst-1", "t1", "c1", 200, ["id"])
        assert ex.result == TestResult.FAILED
        assert "name" in ex.missing_fields

    def test_pass_rate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerContractTest()
        svc.add_test("inst-1", ContractTest(test_id="t1", consumer_id="c1", endpoint="/a", method="GET", expected_status=200))
        svc.execute("inst-1", "t1", "c1", 200, [])
        svc.execute("inst-1", "t1", "c1", 500, [])
        assert svc.pass_rate("inst-1", "c1") == 50.0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerContractTest()
        svc.add_test("inst-1", ContractTest(test_id="t1", consumer_id="c1", endpoint="/a", method="GET", expected_status=200))
        assert svc.test_count("inst-2") == 0
