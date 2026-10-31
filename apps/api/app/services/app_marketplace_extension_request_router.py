"""Request Router — content-based routing with weighted targets and canary.

Implements:
- Route rules matching on method, path, headers, query params
- Weighted traffic splitting across targets (A/B, canary)
- Header-based routing (feature flags, tenant isolation)
- Fallback chains (primary → secondary → default)
- Request mirroring (shadow traffic for testing)
"""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import re


@dataclass
class RouteTarget:
    name: str
    weight: int = 100  # percentage (0-100)
    url: str = ""
    mirror: bool = False  # shadow traffic (fire-and-forget)


@dataclass
class RouteRule:
    rule_id: str
    priority: int = 0
    match_method: str = ""  # empty = any
    match_path: str = ""    # regex pattern
    match_headers: dict[str, str] = field(default_factory=dict)
    targets: list[RouteTarget] = field(default_factory=list)
    fallback: str = ""


@dataclass
class RoutingDecision:
    target: str
    rule_id: str
    mirrors: list[str] = field(default_factory=list)
    reason: str = ""


class RequestRouterService:
    def __init__(self):
        self._rules: list[RouteRule] = []
        self._default_target: str = "default"

    def add_rule(self, rule: RouteRule) -> None:
        self._rules.append(rule)
        self._rules.sort(key=lambda r: r.priority, reverse=True)

    def set_default(self, target: str) -> None:
        self._default_target = target

    def route(self, method: str, path: str, headers: dict | None = None,
              routing_key: str = "") -> RoutingDecision:
        """Route a request to the best target."""
        headers = headers or {}

        for rule in self._rules:
            if self._matches(rule, method, path, headers):
                target = self._select_target(rule.targets, routing_key or path)
                mirrors = [t.name for t in rule.targets if t.mirror]

                if target:
                    return RoutingDecision(
                        target=target.name, rule_id=rule.rule_id,
                        mirrors=mirrors,
                        reason=f"Matched rule {rule.rule_id}")

                # Fallback
                if rule.fallback:
                    return RoutingDecision(
                        target=rule.fallback, rule_id=rule.rule_id,
                        reason="Fallback target")

        return RoutingDecision(target=self._default_target, rule_id="",
                               reason="Default route")

    def _matches(self, rule: RouteRule, method: str, path: str,
                 headers: dict) -> bool:
        if rule.match_method and rule.match_method.upper() != method.upper():
            return False
        if rule.match_path:
            if not re.match(rule.match_path, path):
                return False
        for header_key, header_val in rule.match_headers.items():
            actual = headers.get(header_key, "")
            if header_val.startswith("regex:"):
                if not re.search(header_val[6:], actual):
                    return False
            elif actual != header_val:
                return False
        return True

    def _select_target(self, targets: list[RouteTarget],
                       routing_key: str) -> RouteTarget | None:
        """Select target by weight using consistent hashing."""
        non_mirror = [t for t in targets if not t.mirror]
        if not non_mirror:
            return None
        if len(non_mirror) == 1:
            return non_mirror[0]

        # Weighted selection via hash
        h = int(hashlib.md5(routing_key.encode()).hexdigest()[:8], 16) % 100
        cumulative = 0
        for target in non_mirror:
            cumulative += target.weight
            if h < cumulative:
                return target
        return non_mirror[-1]

    def get_rules(self) -> list[dict]:
        return [{"rule_id": r.rule_id, "priority": r.priority,
                 "targets": [t.name for t in r.targets if not t.mirror],
                 "mirrors": [t.name for t in r.targets if t.mirror]}
                for r in self._rules]
