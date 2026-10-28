"""App API Header Policy — enforce required/forbidden response headers.

Manages header policies:
- Define required response headers
- Define forbidden headers to strip
- Validate responses against policy
- Per-installation scoped policies
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class HeaderRule:
    """A header policy rule."""

    rule_id: str
    header_name: str
    action: str  # "require", "forbid", "set_default"
    value: str = ""  # default value for set_default


class AppAPIHeaderPolicy:
    """Enforce required/forbidden response headers."""

    def __init__(self) -> None:
        self._rules: dict[tuple[str, str], HeaderRule] = {}

    def add_rule(
        self, installation_id: str, rule_id: str, header_name: str,
        action: str, value: str = "",
    ) -> HeaderRule:
        if not installation_id:
            raise ValueError("installation_id is required")
        if action not in ("require", "forbid", "set_default"):
            raise ValueError("action must be require, forbid, or set_default")

        rule = HeaderRule(rule_id=rule_id, header_name=header_name, action=action, value=value)
        self._rules[(installation_id, rule_id)] = rule
        return rule

    def apply_policy(self, installation_id: str, headers: dict[str, str]) -> dict:
        """Apply policy to headers. Returns {headers, violations}."""
        result = dict(headers)
        violations: list[str] = []
        rules = [r for (inst, _), r in self._rules.items() if inst == installation_id]

        for rule in rules:
            lower_keys = {k.lower(): k for k in result}
            header_lower = rule.header_name.lower()

            if rule.action == "require":
                if header_lower not in lower_keys:
                    violations.append(f"Missing required header: {rule.header_name}")
            elif rule.action == "forbid":
                if header_lower in lower_keys:
                    del result[lower_keys[header_lower]]
                    violations.append(f"Stripped forbidden header: {rule.header_name}")
            elif rule.action == "set_default":
                if header_lower not in lower_keys:
                    result[rule.header_name] = rule.value

        return {"headers": result, "violations": violations}

    def list_rules(self, installation_id: str) -> list[HeaderRule]:
        return [r for (inst, _), r in self._rules.items() if inst == installation_id]
