"""API Request Validator Middleware — validate incoming requests before processing."""
from __future__ import annotations
from dataclasses import dataclass, field
import re
import structlog

log = structlog.get_logger()

@dataclass
class ValidationMiddlewareRule:
    rule_id: str
    target: str  # "header", "query", "body", "path"
    field_name: str
    check: str  # "required", "regex", "max_length", "min_length", "type"
    config: dict[str, str] = field(default_factory=dict)

@dataclass
class MiddlewareResult:
    valid: bool
    errors: list[str] = field(default_factory=list)
    rules_checked: int = 0

VALID_TARGETS = {"header", "query", "body", "path"}
VALID_CHECKS = {"required", "regex", "max_length", "min_length", "type"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestValidatorMiddleware:
    def __init__(self) -> None:
        self._rules: dict[tuple[str, str], list[ValidationMiddlewareRule]] = {}
        self._stats: dict[str, dict[str, int]] = {}

    def add_rule(self, installation_id: str, endpoint: str, rule: ValidationMiddlewareRule) -> ValidationMiddlewareRule:
        if not installation_id: raise ValueError("installation_id is required")
        if rule.target not in VALID_TARGETS: raise ValueError(f"Invalid target: {rule.target}")
        if rule.check not in VALID_CHECKS: raise ValueError(f"Invalid check: {rule.check}")
        if rule.check == "regex":
            re.compile(str(rule.config.get("pattern", "")))
        self._rules.setdefault((installation_id, endpoint), []).append(rule)
        return rule

    def validate_request(self, installation_id: str, endpoint: str, headers: dict[str, str] | None = None, query: dict[str, str] | None = None, body: dict | None = None) -> MiddlewareResult:
        rules = self._rules.get((installation_id, endpoint), [])
        errors: list[str] = []
        sources = {"header": {k.lower(): v for k, v in (headers or {}).items()}, "query": query or {}, "body": body or {}}
        for r in rules:
            source = sources.get(r.target, {})
            val = source.get(r.field_name.lower() if r.target == "header" else r.field_name)
            if r.check == "required" and val is None:
                errors.append(f"{r.target}.{r.field_name} is required")
            elif r.check == "regex" and val is not None:
                if not re.match(str(r.config.get("pattern", "")), str(val)):
                    errors.append(f"{r.target}.{r.field_name} fails regex")
            elif r.check == "min_length" and val is not None:
                if len(str(val)) < int(r.config.get("min", 0)):
                    errors.append(f"{r.target}.{r.field_name} below min length")
            elif r.check == "max_length" and val is not None:
                if len(str(val)) > int(r.config.get("max", 9999)):
                    errors.append(f"{r.target}.{r.field_name} exceeds max length")
        stats = self._stats.setdefault(installation_id, {"checked": 0, "rejected": 0})
        stats["checked"] += 1
        if errors: stats["rejected"] += 1
        return MiddlewareResult(valid=len(errors) == 0, errors=errors, rules_checked=len(rules))

    def rejection_rate(self, installation_id: str) -> float:
        s = self._stats.get(installation_id, {"checked": 0, "rejected": 0})
        if s["checked"] == 0: return 0.0
        return round((s["rejected"] / s["checked"]) * 100, 1)

    def rule_count(self, installation_id: str) -> int:
        return sum(len(rs) for (inst, _), rs in self._rules.items() if inst == installation_id)
