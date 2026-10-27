"""API Contract Tester — consumer-driven contract verification.

Pact-style contract testing: consumers define expectations,
providers verify they meet them.

Implements:
- Contract definition: request → expected response
- Provider verification against contracts
- Schema matching (type, structure, not exact values)
- Backward compatibility checking
- Contract versioning
"""
from __future__ import annotations
from dataclasses import dataclass, field
import re


@dataclass
class RequestContract:
    method: str
    path: str
    headers: dict[str, str] = field(default_factory=dict)
    body: dict | None = None


@dataclass
class ResponseContract:
    status: int
    body_schema: dict = field(default_factory=dict)  # {field: type_name}
    required_fields: list[str] = field(default_factory=list)
    headers: dict[str, str] = field(default_factory=dict)


@dataclass
class Contract:
    contract_id: str
    consumer: str
    provider: str
    description: str
    request: RequestContract
    response: ResponseContract
    version: int = 1


@dataclass
class VerificationResult:
    contract_id: str
    passed: bool
    errors: list[str] = field(default_factory=list)


class ContractTesterService:
    TYPE_VALIDATORS = {
        "string": lambda v: isinstance(v, str),
        "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
        "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
        "boolean": lambda v: isinstance(v, bool),
        "array": lambda v: isinstance(v, list),
        "object": lambda v: isinstance(v, dict),
        "any": lambda v: True,
    }

    def __init__(self):
        self._contracts: dict[str, Contract] = {}
        self._counter = 0

    def define_contract(self, consumer: str, provider: str, description: str,
                        request: RequestContract,
                        response: ResponseContract) -> Contract:
        self._counter += 1
        contract = Contract(contract_id=f"pact-{self._counter}",
                            consumer=consumer, provider=provider,
                            description=description,
                            request=request, response=response)
        self._contracts[contract.contract_id] = contract
        return contract

    def verify(self, contract_id: str, actual_status: int,
               actual_body: dict, actual_headers: dict | None = None) -> VerificationResult:
        """Verify a provider response against a contract."""
        contract = self._contracts.get(contract_id)
        if not contract:
            return VerificationResult(contract_id, False, ["Contract not found"])

        errors = []

        # Status code
        if actual_status != contract.response.status:
            errors.append(f"Status: expected {contract.response.status}, got {actual_status}")

        # Required fields
        for field_name in contract.response.required_fields:
            if field_name not in actual_body:
                errors.append(f"Missing required field: {field_name}")

        # Type checking
        for field_name, expected_type in contract.response.body_schema.items():
            if field_name not in actual_body:
                if field_name in contract.response.required_fields:
                    continue  # already reported as missing
                continue  # optional field
            value = actual_body[field_name]
            validator = self.TYPE_VALIDATORS.get(expected_type)
            if validator and not validator(value):
                errors.append(f"Type mismatch: {field_name} expected {expected_type}, "
                              f"got {type(value).__name__}")

        # Response headers
        actual_headers = actual_headers or {}
        for header, expected_val in contract.response.headers.items():
            actual_val = actual_headers.get(header, "")
            if expected_val and actual_val != expected_val:
                errors.append(f"Header {header}: expected '{expected_val}', got '{actual_val}'")

        return VerificationResult(contract_id, len(errors) == 0, errors)

    def verify_all(self, provider: str, handler: callable) -> list[VerificationResult]:
        """Verify all contracts for a provider using a handler function.
        handler(request) -> (status, body, headers)"""
        results = []
        for contract in self._contracts.values():
            if contract.provider != provider:
                continue
            status, body, headers = handler(contract.request)
            result = self.verify(contract.contract_id, status, body, headers)
            results.append(result)
        return results

    def check_backward_compat(self, old_contract_id: str,
                              new_body_schema: dict,
                              new_required: list[str]) -> list[str]:
        """Check if schema change is backward compatible for consumers."""
        old = self._contracts.get(old_contract_id)
        if not old:
            return ["Old contract not found"]

        issues = []
        old_schema = old.response.body_schema
        old_required = set(old.response.required_fields)

        # Removed fields that consumers expect
        for field_name in old_schema:
            if field_name not in new_body_schema:
                issues.append(f"Removed field '{field_name}' that consumers expect")

        # Changed types
        for field_name in old_schema:
            if field_name in new_body_schema:
                if old_schema[field_name] != new_body_schema[field_name]:
                    issues.append(f"Type changed: {field_name} from {old_schema[field_name]} to {new_body_schema[field_name]}")

        # New required fields (consumers won't send them)
        for field_name in new_required:
            if field_name not in old_required and field_name not in old_schema:
                issues.append(f"New required field '{field_name}' breaks existing consumers")

        return issues

    def get_contracts_for(self, provider: str) -> list[Contract]:
        return [c for c in self._contracts.values() if c.provider == provider]
