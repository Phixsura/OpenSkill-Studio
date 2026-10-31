"""App API Developer API Output Transformer — transform API responses before delivery."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class TransformRule:
    rule_id: str
    operation: str  # "rename", "remove", "add", "format_date", "mask"
    field: str
    config: dict[str, str] = field(default_factory=dict)
    applied_count: int = 0

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiOutputTransformer:
    def __init__(self) -> None:
        self._rules: dict[tuple[str, str], list[TransformRule]] = {}

    def add_rule(self, installation_id: str, endpoint: str, rule_id: str, operation: str, field_name: str, config: dict[str, str] | None = None) -> TransformRule:
        if not installation_id: raise ValueError("installation_id is required")
        valid = {"rename", "remove", "add", "format_date", "mask"}
        if operation not in valid: raise ValueError(f"Invalid operation: {operation}")
        r = TransformRule(rule_id=rule_id, operation=operation, field=field_name, config=config or {})
        self._rules.setdefault((installation_id, endpoint), []).append(r)
        return r

    def transform(self, installation_id: str, endpoint: str, response: dict) -> dict:
        rules = self._rules.get((installation_id, endpoint), [])
        result = dict(response)
        for r in rules:
            r.applied_count += 1
            if r.operation == "remove": result.pop(r.field, None)
            elif r.operation == "rename" and r.field in result:
                result[r.config.get("to", r.field)] = result.pop(r.field)
            elif r.operation == "add":
                result[r.field] = r.config.get("value", "")
            elif r.operation == "mask" and r.field in result:
                val = str(result[r.field])
                result[r.field] = "***" + val[-4:] if len(val) > 4 else "***"
        return result

    def rules_for(self, installation_id: str, endpoint: str) -> list[TransformRule]:
        return self._rules.get((installation_id, endpoint), [])

    def total_transforms(self, installation_id: str) -> int:
        return sum(r.applied_count for (inst, _ep), rules in self._rules.items() if inst == installation_id for r in rules)
