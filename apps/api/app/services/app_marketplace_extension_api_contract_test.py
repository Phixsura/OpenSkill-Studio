"""API Contract Test — validate API contracts between extensions.

Defines expected request/response contracts, validates actual API
behavior against contracts, tracks contract violations, and generates
compatibility reports.
"""
from __future__ import annotations
import json
import secrets
from dataclasses import dataclass, field
from enum import Enum


class ContractResult(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"


@dataclass
class ContractExpectation:
    field: str
    expected_type: str  # string, integer, boolean, array, object
    required: bool = True
    nullable: bool = False


@dataclass
class ApiContract:
    contract_id: str
    provider: str  # extension providing the API
    consumer: str  # extension consuming the API
    endpoint: str
    method: str
    request_contract: list[ContractExpectation] = field(default_factory=list)
    response_contract: list[ContractExpectation] = field(default_factory=list)
    status_code: int = 200


@dataclass
class ContractTestResult:
    contract_id: str
    result: ContractResult
    violations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


TYPE_CHECK = {
    "string": lambda v: isinstance(v, str),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
    "array": lambda v: isinstance(v, list),
    "object": lambda v: isinstance(v, dict),
}


class ApiContractTestService:
    """Validates API contracts between provider and consumer extensions."""

    def __init__(self):
        self._contracts: dict[str, ApiContract] = {}
        self._results: list[ContractTestResult] = []

    def define_contract(self, provider: str, consumer: str,
                        endpoint: str, method: str,
                        request_fields: list[dict] | None = None,
                        response_fields: list[dict] | None = None,
                        status_code: int = 200) -> ApiContract:
        contract_id = f"ct_{secrets.token_urlsafe(8)}"
        req = [ContractExpectation(
            field=f["field"], expected_type=f["type"],
            required=f.get("required", True), nullable=f.get("nullable", False),
        ) for f in (request_fields or [])]
        resp = [ContractExpectation(
            field=f["field"], expected_type=f["type"],
            required=f.get("required", True), nullable=f.get("nullable", False),
        ) for f in (response_fields or [])]

        contract = ApiContract(
            contract_id=contract_id, provider=provider, consumer=consumer,
            endpoint=endpoint, method=method.upper(),
            request_contract=req, response_contract=resp,
            status_code=status_code,
        )
        self._contracts[contract_id] = contract
        return contract

    def validate_response(self, contract_id: str, response_data: dict,
                          actual_status: int = 200) -> ContractTestResult:
        contract = self._contracts.get(contract_id)
        if not contract:
            return ContractTestResult(contract_id=contract_id, result=ContractResult.FAIL,
                                     violations=["Contract not found"])

        violations: list[str] = []
        warnings: list[str] = []

        if actual_status != contract.status_code:
            violations.append(f"Status: expected {contract.status_code}, got {actual_status}")

        for exp in contract.response_contract:
            value = response_data.get(exp.field)
            if value is None:
                if exp.required and not exp.nullable:
                    violations.append(f"Missing required field: {exp.field}")
                continue
            checker = TYPE_CHECK.get(exp.expected_type)
            if checker and not checker(value):
                violations.append(f"{exp.field}: expected {exp.expected_type}, got {type(value).__name__}")

        # Warn about extra fields
        expected_fields = {e.field for e in contract.response_contract}
        for key in response_data:
            if key not in expected_fields:
                warnings.append(f"Unexpected field: {key}")

        result = ContractResult.FAIL if violations else (
            ContractResult.WARN if warnings else ContractResult.PASS)
        tr = ContractTestResult(
            contract_id=contract_id, result=result,
            violations=violations, warnings=warnings,
        )
        self._results.append(tr)
        return tr

    def get_compatibility(self, provider: str, consumer: str) -> dict:
        contracts = [c for c in self._contracts.values()
                     if c.provider == provider and c.consumer == consumer]
        results = [r for r in self._results
                   if r.contract_id in {c.contract_id for c in contracts}]
        passed = sum(1 for r in results if r.result == ContractResult.PASS)
        total = len(results)
        return {
            "provider": provider, "consumer": consumer,
            "contracts": len(contracts), "tests_run": total,
            "passed": passed, "failed": total - passed,
            "compatible": passed == total if total else True,
        }

    def list_contracts(self, extension_id: str) -> list[ApiContract]:
        return [c for c in self._contracts.values()
                if c.provider == extension_id or c.consumer == extension_id]
