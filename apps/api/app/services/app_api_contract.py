"""App API Contract — define and validate API contracts.

Manages API contracts:
- Define request/response contracts per endpoint
- Validate payloads against contracts
- Track contract violation counts
- Per-installation scoped contracts
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class FieldSpec:
    """A field specification in a contract."""

    name: str
    field_type: str  # "string", "int", "float", "bool", "list", "object"
    required: bool = True


@dataclass
class APIContract:
    """An API contract definition."""

    contract_id: str
    method: str
    path: str
    request_fields: list[FieldSpec] = field(default_factory=list)
    response_fields: list[FieldSpec] = field(default_factory=list)
    violation_count: int = 0


TYPE_MAP = {"string": str, "int": int, "float": (int, float), "bool": bool, "list": list, "object": dict}


class AppAPIContract:
    """Define and validate API contracts."""

    def __init__(self) -> None:
        self._contracts: dict[tuple[str, str], APIContract] = {}

    def define(
        self, installation_id: str, contract_id: str, method: str, path: str,
        request_fields: list[dict] | None = None,
        response_fields: list[dict] | None = None,
    ) -> APIContract:
        if not installation_id:
            raise ValueError("installation_id is required")

        req = [FieldSpec(name=f["name"], field_type=f["type"], required=f.get("required", True)) for f in (request_fields or [])]
        resp = [FieldSpec(name=f["name"], field_type=f["type"], required=f.get("required", True)) for f in (response_fields or [])]

        contract = APIContract(
            contract_id=contract_id, method=method.upper(), path=path,
            request_fields=req, response_fields=resp,
        )
        self._contracts[(installation_id, contract_id)] = contract
        return contract

    def validate_payload(
        self, installation_id: str, contract_id: str,
        payload: dict, direction: str = "request",
    ) -> list[str]:
        """Validate payload. Returns list of violation messages."""
        c = self._get(installation_id, contract_id)
        fields = c.request_fields if direction == "request" else c.response_fields
        errors: list[str] = []

        for spec in fields:
            if spec.name not in payload:
                if spec.required:
                    errors.append(f"Missing required field: {spec.name}")
                continue
            val = payload[spec.name]
            # bool-before-int guard
            if spec.field_type in ("int", "float") and isinstance(val, bool):
                errors.append(f"{spec.name}: expected {spec.field_type}, got bool")
                continue
            expected = TYPE_MAP.get(spec.field_type)
            if expected and not isinstance(val, expected):
                errors.append(f"{spec.name}: expected {spec.field_type}, got {type(val).__name__}")

        if errors:
            c.violation_count += len(errors)
        return errors

    def list_contracts(self, installation_id: str) -> list[APIContract]:
        return [c for (inst, _), c in self._contracts.items() if inst == installation_id]

    def _get(self, installation_id: str, contract_id: str) -> APIContract:
        key = (installation_id, contract_id)
        c = self._contracts.get(key)
        if c is None:
            raise KeyError(f"Contract {contract_id} not found")
        return c
