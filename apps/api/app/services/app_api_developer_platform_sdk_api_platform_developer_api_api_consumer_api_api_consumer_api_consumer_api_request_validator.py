"""Consumer API Request Validator — validate incoming requests against schemas."""
from __future__ import annotations
from dataclasses import dataclass, field
import json
import structlog

log = structlog.get_logger()

@dataclass
class ValidationRule:
    field_path: str
    rule_type: str  # "required", "type", "pattern", "min", "max", "enum"
    value: str = ""  # rule parameter

@dataclass
class EndpointValidation:
    endpoint_path: str
    method: str
    rules: list[ValidationRule] = field(default_factory=list)

@dataclass
class ValidationError:
    field: str
    rule: str
    message: str

@dataclass
class ValidationResult:
    valid: bool
    errors: list[ValidationError] = field(default_factory=list)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRequestValidator:
    def __init__(self) -> None:
        self._validations: dict[tuple[str, str, str], EndpointValidation] = {}  # (inst, path, method)

    def register(self, installation_id: str, validation: EndpointValidation) -> EndpointValidation:
        if not installation_id:
            raise ValueError("installation_id is required")
        key = (installation_id, validation.endpoint_path, validation.method.upper())
        self._validations[key] = validation
        return validation

    def validate(self, installation_id: str, endpoint_path: str, method: str, body: dict) -> ValidationResult:
        key = (installation_id, endpoint_path, method.upper())
        validation = self._validations.get(key)
        if not validation:
            return ValidationResult(valid=True)
        errors: list[ValidationError] = []
        for rule in validation.rules:
            val = body.get(rule.field_path)
            if rule.rule_type == "required" and val is None:
                errors.append(ValidationError(field=rule.field_path, rule="required", message=f"{rule.field_path} is required"))
            elif rule.rule_type == "type" and val is not None:
                expected = rule.value
                if expected == "string" and not isinstance(val, str):
                    errors.append(ValidationError(field=rule.field_path, rule="type", message=f"{rule.field_path} must be a string"))
                elif expected == "integer" and (not isinstance(val, int) or isinstance(val, bool)):
                    errors.append(ValidationError(field=rule.field_path, rule="type", message=f"{rule.field_path} must be an integer"))
                elif expected == "boolean" and not isinstance(val, bool):
                    errors.append(ValidationError(field=rule.field_path, rule="type", message=f"{rule.field_path} must be a boolean"))
            elif rule.rule_type == "min" and val is not None and isinstance(val, (int, float)) and not isinstance(val, bool):
                if val < float(rule.value):
                    errors.append(ValidationError(field=rule.field_path, rule="min", message=f"{rule.field_path} must be >= {rule.value}"))
            elif rule.rule_type == "max" and val is not None and isinstance(val, (int, float)) and not isinstance(val, bool):
                if val > float(rule.value):
                    errors.append(ValidationError(field=rule.field_path, rule="max", message=f"{rule.field_path} must be <= {rule.value}"))
            elif rule.rule_type == "enum" and val is not None:
                allowed = rule.value.split(",")
                if str(val) not in allowed:
                    errors.append(ValidationError(field=rule.field_path, rule="enum", message=f"{rule.field_path} must be one of {rule.value}"))
        return ValidationResult(valid=len(errors) == 0, errors=errors)

    def list_validations(self, installation_id: str) -> list[EndpointValidation]:
        return [v for (inst, _, _), v in self._validations.items() if inst == installation_id]
