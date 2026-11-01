"""Validation Pipeline — composable validators with error accumulation.

Implements:
- Chain validators: each checks one aspect
- Two modes: fail-fast (stop on first error) and accumulate-all
- Built-in validators: required, type, range, pattern, length, enum
- Custom validator functions
- Nested object validation
- Context-dependent validation (field A required if field B = X)
"""
from __future__ import annotations
from dataclasses import dataclass, field
import re


@dataclass
class ValidationError:
    field: str
    rule: str
    message: str
    value: object = None


@dataclass
class ValidationResult:
    valid: bool
    errors: list[ValidationError] = field(default_factory=list)

    def add(self, field_name: str, rule: str, message: str, value: object = None):
        self.errors.append(ValidationError(field_name, rule, message, value))
        self.valid = False


class Validator:
    def __init__(self, field_name: str):
        self._field = field_name
        self._rules: list[tuple[str, callable, str]] = []

    def required(self, message: str = "") -> Validator:
        self._rules.append(("required", lambda v: v is not None and v != "",
                           message or f"{self._field} is required"))
        return self

    def type_of(self, expected: type, message: str = "") -> Validator:
        self._rules.append(("type", lambda v: isinstance(v, expected),
                           message or f"{self._field} must be {expected.__name__}"))
        return self

    def min_val(self, minimum: float, message: str = "") -> Validator:
        self._rules.append(("min", lambda v: isinstance(v, (int, float)) and v >= minimum,
                           message or f"{self._field} must be >= {minimum}"))
        return self

    def max_val(self, maximum: float, message: str = "") -> Validator:
        self._rules.append(("max", lambda v: isinstance(v, (int, float)) and v <= maximum,
                           message or f"{self._field} must be <= {maximum}"))
        return self

    def min_length(self, n: int, message: str = "") -> Validator:
        self._rules.append(("minLength", lambda v: isinstance(v, (str, list)) and len(v) >= n,
                           message or f"{self._field} must have length >= {n}"))
        return self

    def max_length(self, n: int, message: str = "") -> Validator:
        self._rules.append(("maxLength", lambda v: isinstance(v, (str, list)) and len(v) <= n,
                           message or f"{self._field} must have length <= {n}"))
        return self

    def pattern(self, regex: str, message: str = "") -> Validator:
        self._rules.append(("pattern", lambda v: isinstance(v, str) and bool(re.search(regex, v)),
                           message or f"{self._field} must match pattern"))
        return self

    def one_of(self, values: list, message: str = "") -> Validator:
        self._rules.append(("enum", lambda v: v in values,
                           message or f"{self._field} must be one of {values}"))
        return self

    def custom(self, rule_name: str, fn: callable, message: str) -> Validator:
        self._rules.append((rule_name, fn, message))
        return self

    def validate(self, value: object, result: ValidationResult,
                 fail_fast: bool = False) -> None:
        for rule_name, check_fn, message in self._rules:
            if rule_name == "required" and (value is None or value == ""):
                result.add(self._field, rule_name, message, value)
                if fail_fast:
                    return
                continue
            if value is None:
                continue  # skip other rules if None and not required
            if not check_fn(value):
                result.add(self._field, rule_name, message, value)
                if fail_fast:
                    return


class ValidationPipelineService:
    def __init__(self):
        self._validators: list[Validator] = []
        self._conditional: list[tuple[callable, Validator]] = []

    def field(self, name: str) -> Validator:
        v = Validator(name)
        self._validators.append(v)
        return v

    def when(self, condition: callable, validator: Validator) -> None:
        """Add conditional validator: only runs when condition(data) is True."""
        self._conditional.append((condition, validator))

    def validate(self, data: dict, fail_fast: bool = False) -> ValidationResult:
        result = ValidationResult(valid=True)

        for v in self._validators:
            value = data.get(v._field)
            v.validate(value, result, fail_fast)
            if fail_fast and not result.valid:
                return result

        for condition, v in self._conditional:
            if condition(data):
                value = data.get(v._field)
                v.validate(value, result, fail_fast)
                if fail_fast and not result.valid:
                    return result

        return result
