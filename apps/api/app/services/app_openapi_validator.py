"""App OpenAPI Validator — validate API responses against OpenAPI schemas.

Validates API behavior against declared contracts:
- Register endpoint schemas
- Validate responses against schemas
- Track compliance per endpoint
- Per-installation scoped schemas
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class EndpointSchema:
    """Schema for an API endpoint."""

    method: str
    path: str
    response_fields: dict[str, str]  # field → expected type
    required_fields: list[str] = field(default_factory=list)


@dataclass
class ValidationViolation:
    """A schema violation."""

    field: str
    expected: str
    actual: str
    message: str


@dataclass
class ContractResult:
    """Result of validating against a contract."""

    method: str
    path: str
    valid: bool
    violations: list[ValidationViolation]


class AppOpenAPIValidator:
    """Validate API responses against OpenAPI schemas."""

    def __init__(self) -> None:
        # (installation_id, method, path) → EndpointSchema
        self._schemas: dict[tuple[str, str, str], EndpointSchema] = {}
        # (installation_id, method, path) → (total, passed)
        self._stats: dict[tuple[str, str, str], tuple[int, int]] = {}

    def register_schema(
        self,
        installation_id: str,
        method: str,
        path: str,
        response_fields: dict[str, str],
        required_fields: list[str] | None = None,
    ) -> EndpointSchema:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not method or not path:
            raise ValueError("method and path are required")

        schema = EndpointSchema(
            method=method.upper(), path=path,
            response_fields=response_fields,
            required_fields=required_fields or [],
        )
        self._schemas[(installation_id, method.upper(), path)] = schema
        return schema

    def validate_response(
        self,
        installation_id: str,
        method: str,
        path: str,
        response: dict,
    ) -> ContractResult:
        key = (installation_id, method.upper(), path)
        schema = self._schemas.get(key)
        if schema is None:
            raise KeyError(f"No schema for {method.upper()} {path}")

        violations: list[ValidationViolation] = []

        # Check required fields
        for rf in schema.required_fields:
            if rf not in response:
                violations.append(ValidationViolation(
                    field=rf, expected="present", actual="missing",
                    message=f"Required field '{rf}' is missing",
                ))

        # Check field types
        type_map = {"string": str, "int": int, "float": (int, float), "bool": bool, "list": list, "object": dict}
        for fname, ftype in schema.response_fields.items():
            if fname not in response:
                continue
            val = response[fname]
            # bool subclass of int guard — check before type map
            if ftype in ("int", "float") and isinstance(val, bool):
                violations.append(ValidationViolation(
                    field=fname, expected=ftype, actual="bool",
                    message=f"Field '{fname}' expected {ftype}, got bool",
                ))
                continue
            expected_type = type_map.get(ftype)
            if expected_type and not isinstance(val, expected_type):
                violations.append(ValidationViolation(
                    field=fname, expected=ftype, actual=type(val).__name__,
                    message=f"Field '{fname}' expected {ftype}",
                ))

        valid = len(violations) == 0

        # Track stats
        total, passed = self._stats.get(key, (0, 0))
        self._stats[key] = (total + 1, passed + (1 if valid else 0))

        return ContractResult(
            method=method.upper(), path=path,
            valid=valid, violations=violations,
        )

    def compliance_rate(self, installation_id: str, method: str, path: str) -> float:
        key = (installation_id, method.upper(), path)
        total, passed = self._stats.get(key, (0, 0))
        return round(passed / total * 100, 1) if total > 0 else 100.0

    def list_schemas(self, installation_id: str) -> list[EndpointSchema]:
        return [s for (inst, _, _), s in self._schemas.items() if inst == installation_id]
