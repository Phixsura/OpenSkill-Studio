"""Consumer API Contract Test — define and verify API contracts."""
from __future__ import annotations
from dataclasses import dataclass, field
import json
import structlog

log = structlog.get_logger()

@dataclass
class ContractAssertion:
    field_path: str
    assertion_type: str  # "exists", "type", "equals", "contains"
    expected_value: str = ""

@dataclass
class APIContract:
    contract_id: str
    endpoint_path: str
    method: str
    description: str = ""
    request_assertions: list[ContractAssertion] = field(default_factory=list)
    response_assertions: list[ContractAssertion] = field(default_factory=list)

@dataclass
class ContractVerifyResult:
    contract_id: str
    passed: bool
    failures: list[str] = field(default_factory=list)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiContractTest:
    def __init__(self) -> None:
        self._contracts: dict[tuple[str, str], APIContract] = {}

    def define(self, installation_id: str, contract: APIContract) -> APIContract:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not contract.response_assertions:
            raise ValueError("At least one response assertion required")
        key = (installation_id, contract.contract_id)
        self._contracts[key] = contract
        return contract

    def verify(self, installation_id: str, contract_id: str, response_body: dict, response_status: int) -> ContractVerifyResult:
        key = (installation_id, contract_id)
        contract = self._contracts.get(key)
        if not contract:
            raise ValueError("Contract not found")
        failures: list[str] = []
        for assertion in contract.response_assertions:
            value = response_body.get(assertion.field_path)
            if assertion.assertion_type == "exists":
                if value is None:
                    failures.append(f"{assertion.field_path}: expected to exist")
            elif assertion.assertion_type == "type":
                type_map = {"string": str, "integer": int, "boolean": bool, "list": list, "object": dict}
                expected_type = type_map.get(assertion.expected_value)
                if expected_type and not isinstance(value, expected_type):
                    failures.append(f"{assertion.field_path}: expected {assertion.expected_value}, got {type(value).__name__}")
            elif assertion.assertion_type == "equals":
                if str(value) != assertion.expected_value:
                    failures.append(f"{assertion.field_path}: expected '{assertion.expected_value}', got '{value}'")
            elif assertion.assertion_type == "contains":
                if not isinstance(value, str) or assertion.expected_value not in value:
                    failures.append(f"{assertion.field_path}: expected to contain '{assertion.expected_value}'")
        return ContractVerifyResult(contract_id=contract_id, passed=len(failures) == 0, failures=failures)

    def list_contracts(self, installation_id: str) -> list[APIContract]:
        return [c for (inst, _), c in self._contracts.items() if inst == installation_id]
