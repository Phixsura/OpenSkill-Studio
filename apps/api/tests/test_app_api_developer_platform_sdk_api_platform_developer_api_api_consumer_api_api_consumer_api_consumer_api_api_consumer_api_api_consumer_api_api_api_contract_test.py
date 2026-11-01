import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_api_consumer_api_api_api_contract_test import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiContractTest, APIContract, ContractAssertion,
)

class TestApiContractTest:
    def test_pass(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiContractTest()
        svc.define("inst-1", APIContract(contract_id="c1", endpoint_path="/api/users", method="GET", response_assertions=[
            ContractAssertion(field_path="data", assertion_type="exists"),
            ContractAssertion(field_path="status", assertion_type="equals", expected_value="ok"),
        ]))
        result = svc.verify("inst-1", "c1", {"data": [1, 2], "status": "ok"}, 200)
        assert result.passed

    def test_fail_missing(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiContractTest()
        svc.define("inst-1", APIContract(contract_id="c1", endpoint_path="/api", method="GET", response_assertions=[ContractAssertion(field_path="data", assertion_type="exists")]))
        result = svc.verify("inst-1", "c1", {}, 200)
        assert not result.passed and "exist" in result.failures[0]

    def test_type_check(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiContractTest()
        svc.define("inst-1", APIContract(contract_id="c1", endpoint_path="/api", method="GET", response_assertions=[ContractAssertion(field_path="count", assertion_type="type", expected_value="integer")]))
        assert svc.verify("inst-1", "c1", {"count": 5}, 200).passed
        assert not svc.verify("inst-1", "c1", {"count": "five"}, 200).passed

    def test_contains(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiContractTest()
        svc.define("inst-1", APIContract(contract_id="c1", endpoint_path="/api", method="GET", response_assertions=[ContractAssertion(field_path="message", assertion_type="contains", expected_value="success")]))
        assert svc.verify("inst-1", "c1", {"message": "operation success"}, 200).passed

    def test_no_assertions_rejected(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiContractTest()
        with pytest.raises(ValueError, match="At least one"):
            svc.define("inst-1", APIContract(contract_id="c1", endpoint_path="/api", method="GET"))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiContractTest()
        svc.define("inst-1", APIContract(contract_id="c1", endpoint_path="/api", method="GET", response_assertions=[ContractAssertion(field_path="x", assertion_type="exists")]))
        assert len(svc.list_contracts("inst-2")) == 0
