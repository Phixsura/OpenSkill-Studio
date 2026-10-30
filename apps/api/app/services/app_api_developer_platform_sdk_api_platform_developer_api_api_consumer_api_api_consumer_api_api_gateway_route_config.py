"""API Gateway Route Config — define routing rules for API gateway endpoints."""
from __future__ import annotations
from dataclasses import dataclass, field
import re
import structlog

log = structlog.get_logger()

@dataclass
class RouteRule:
    rule_id: str
    path_pattern: str    # e.g. "/api/v1/users/*"
    methods: list[str] = field(default_factory=lambda: ["GET"])
    target_service: str = ""
    strip_prefix: bool = False
    timeout_ms: int = 30000
    auth_required: bool = True
    rate_limit_rps: int | None = None

@dataclass
class MatchResult:
    matched: bool
    rule: RouteRule | None = None
    captured: dict[str, str] = field(default_factory=dict)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiApiGatewayRouteConfig:
    def __init__(self) -> None:
        self._rules: dict[tuple[str, str], RouteRule] = {}

    def add_rule(self, installation_id: str, rule: RouteRule) -> RouteRule:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not rule.target_service:
            raise ValueError("target_service is required")
        key = (installation_id, rule.rule_id)
        if key in self._rules:
            raise ValueError(f"Rule {rule.rule_id} already exists")
        self._rules[key] = rule
        log.info("route_added", installation_id=installation_id, rule_id=rule.rule_id, pattern=rule.path_pattern)
        return rule

    def remove_rule(self, installation_id: str, rule_id: str) -> None:
        key = (installation_id, rule_id)
        if key not in self._rules:
            raise ValueError("Rule not found")
        del self._rules[key]

    def match(self, installation_id: str, method: str, path: str) -> MatchResult:
        for (inst, _), rule in self._rules.items():
            if inst != installation_id:
                continue
            if method.upper() not in [m.upper() for m in rule.methods]:
                continue
            regex = "^" + rule.path_pattern.replace("*", "(.+)") + "$"
            m = re.match(regex, path)
            if m:
                captured = {f"param{i}": g for i, g in enumerate(m.groups())}
                return MatchResult(matched=True, rule=rule, captured=captured)
        return MatchResult(matched=False)

    def list_rules(self, installation_id: str) -> list[RouteRule]:
        return [r for (inst, _), r in self._rules.items() if inst == installation_id]
