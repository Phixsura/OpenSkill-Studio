"""App Rate Limit Policy — per-endpoint rate limit rules for installed apps.

Allows fine-grained per-endpoint rate limiting beyond global API key limits:
- Endpoint-specific rate rules (method + path pattern)
- Burst vs sustained rate differentiation
- Custom response headers
- Exemption lists (internal/admin endpoints)
- Policy evaluation with match ordering
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


@dataclass
class EndpointRateRule:
    """Rate limit rule for a specific endpoint pattern."""

    rule_id: str
    method: str              # GET, POST, * (wildcard)
    path_pattern: str        # exact or glob, e.g. "/api/v1/skills/*"
    requests_per_minute: int
    burst_size: int = 0      # 0 = no burst allowance
    exempt: bool = False     # exempt from rate limiting


@dataclass
class RateLimitDecision:
    """Result of evaluating a request against rate limit policies."""

    allowed: bool
    matched_rule: str | None
    limit: int
    burst: int
    exempt: bool
    headers: dict[str, str]


class AppRateLimitPolicy:
    """Evaluate per-endpoint rate limit policies."""

    def __init__(self):
        # app_id → list of rules (ordered by priority)
        self._policies: dict[str, list[EndpointRateRule]] = {}
        self._next_id = 0

    def add_rule(self, app_id: str, method: str, path_pattern: str,
                 requests_per_minute: int, burst_size: int = 0,
                 exempt: bool = False) -> EndpointRateRule:
        """Add a rate limit rule for an app."""
        if requests_per_minute < 0:
            raise ValueError("requests_per_minute must be non-negative")
        self._next_id += 1
        rule = EndpointRateRule(
            rule_id=f"rl-{self._next_id}",
            method=method.upper(),
            path_pattern=path_pattern,
            requests_per_minute=requests_per_minute,
            burst_size=burst_size,
            exempt=exempt,
        )
        self._policies.setdefault(app_id, []).append(rule)
        return rule

    def remove_rule(self, app_id: str, rule_id: str) -> bool:
        rules = self._policies.get(app_id, [])
        before = len(rules)
        self._policies[app_id] = [r for r in rules if r.rule_id != rule_id]
        return len(self._policies[app_id]) < before

    def evaluate(self, app_id: str, method: str, path: str) -> RateLimitDecision:
        """Evaluate which rate limit rule applies to a request."""
        rules = self._policies.get(app_id, [])

        for rule in rules:
            if self._matches(rule, method, path):
                if rule.exempt:
                    return RateLimitDecision(
                        allowed=True, matched_rule=rule.rule_id,
                        limit=0, burst=0, exempt=True,
                        headers={},
                    )
                return RateLimitDecision(
                    allowed=True, matched_rule=rule.rule_id,
                    limit=rule.requests_per_minute, burst=rule.burst_size,
                    exempt=False,
                    headers={
                        "X-RateLimit-Limit": str(rule.requests_per_minute),
                        "X-RateLimit-Burst": str(rule.burst_size),
                    },
                )

        # No rule matched → no specific limit
        return RateLimitDecision(
            allowed=True, matched_rule=None,
            limit=0, burst=0, exempt=False,
            headers={},
        )

    def get_rules(self, app_id: str) -> list[EndpointRateRule]:
        return list(self._policies.get(app_id, []))

    @staticmethod
    def _matches(rule: EndpointRateRule, method: str, path: str) -> bool:
        # Method match
        if rule.method != "*" and rule.method != method.upper():
            return False
        # Path match: support trailing wildcard
        pattern = rule.path_pattern
        if pattern.endswith("/*"):
            prefix = pattern[:-2]
            return path == prefix or path.startswith(prefix + "/")
        elif pattern.endswith("*"):
            return path.startswith(pattern[:-1])
        return path == pattern
