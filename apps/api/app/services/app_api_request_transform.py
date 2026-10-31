"""App API Request Transform — transform incoming API requests.

Manages request transformations:
- Header injection/removal on inbound requests
- Query parameter defaults
- Path rewriting
- Per-installation scoped transforms
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class RequestTransformRule:
    """A request transformation rule."""

    rule_id: str
    action: str  # "add_header", "remove_header", "add_query", "rewrite_path"
    key: str
    value: str = ""


class AppAPIRequestTransform:
    """Transform incoming API requests."""

    def __init__(self) -> None:
        self._rules: dict[tuple[str, str], RequestTransformRule] = {}

    def add_rule(
        self, installation_id: str, rule_id: str, action: str,
        key: str, value: str = "",
    ) -> RequestTransformRule:
        if not installation_id:
            raise ValueError("installation_id is required")
        if action not in ("add_header", "remove_header", "add_query", "rewrite_path"):
            raise ValueError("invalid action")

        rule = RequestTransformRule(rule_id=rule_id, action=action, key=key, value=value)
        self._rules[(installation_id, rule_id)] = rule
        return rule

    def apply(
        self, installation_id: str, headers: dict, query: dict, path: str,
    ) -> dict:
        """Apply all rules. Returns {headers, query, path}."""
        h = dict(headers)
        q = dict(query)
        p = path

        for (inst, _), rule in self._rules.items():
            if inst != installation_id:
                continue
            if rule.action == "add_header":
                h[rule.key] = rule.value
            elif rule.action == "remove_header":
                h.pop(rule.key, None)
            elif rule.action == "add_query":
                if rule.key not in q:
                    q[rule.key] = rule.value
            elif rule.action == "rewrite_path":
                p = p.replace(rule.key, rule.value)

        return {"headers": h, "query": q, "path": p}

    def list_rules(self, installation_id: str) -> list[RequestTransformRule]:
        return [r for (inst, _), r in self._rules.items() if inst == installation_id]
