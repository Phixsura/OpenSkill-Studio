"""Sandbox Webhook Interceptor — intercept and inspect webhook traffic.

Captures inbound/outbound webhooks for debugging with request/response
replay, conditional breakpoints, and payload modification.
"""
from __future__ import annotations
import secrets
import time
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class InterceptedWebhook:
    intercept_id: str
    direction: str  # inbound, outbound
    url: str
    method: str
    headers: dict[str, str]
    body: str
    status_code: int = 0
    response_body: str = ""
    paused: bool = False
    modified: bool = False
    timestamp: float = 0.0

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.time()


@dataclass
class InterceptRule:
    rule_id: str
    url_pattern: str
    direction: str = "both"
    pause: bool = False  # pause for inspection
    enabled: bool = True


class SandboxWebhookInterceptorService:
    """Intercepts webhook traffic for debugging and inspection."""

    MAX_CAPTURES = 500

    def __init__(self):
        self._captures: dict[str, list[InterceptedWebhook]] = defaultdict(list)
        self._rules: dict[str, list[InterceptRule]] = defaultdict(list)

    def add_rule(self, sandbox_id: str, url_pattern: str,
                 direction: str = "both", pause: bool = False) -> InterceptRule:
        rule = InterceptRule(
            rule_id=f"ir_{secrets.token_urlsafe(6)}",
            url_pattern=url_pattern, direction=direction, pause=pause,
        )
        self._rules[sandbox_id].append(rule)
        return rule

    def intercept(self, sandbox_id: str, direction: str, url: str,
                  method: str, headers: dict[str, str],
                  body: str, status_code: int = 0,
                  response_body: str = "") -> InterceptedWebhook:
        # Check rules
        should_pause = False
        for rule in self._rules.get(sandbox_id, []):
            if not rule.enabled:
                continue
            if rule.direction != "both" and rule.direction != direction:
                continue
            if rule.url_pattern in url:
                if rule.pause:
                    should_pause = True

        capture = InterceptedWebhook(
            intercept_id=f"ic_{secrets.token_urlsafe(8)}",
            direction=direction, url=url, method=method,
            headers=headers, body=body, status_code=status_code,
            response_body=response_body, paused=should_pause,
        )
        captures = self._captures[sandbox_id]
        captures.append(capture)
        if len(captures) > self.MAX_CAPTURES:
            self._captures[sandbox_id] = captures[-self.MAX_CAPTURES:]
        return capture

    def resume(self, sandbox_id: str, intercept_id: str,
               modified_body: str | None = None) -> bool:
        for cap in self._captures.get(sandbox_id, []):
            if cap.intercept_id == intercept_id and cap.paused:
                cap.paused = False
                if modified_body is not None:
                    cap.body = modified_body
                    cap.modified = True
                return True
        return False

    def get_captures(self, sandbox_id: str, direction: str | None = None,
                     limit: int = 50) -> list[InterceptedWebhook]:
        caps = self._captures.get(sandbox_id, [])
        if direction:
            caps = [c for c in caps if c.direction == direction]
        return caps[-limit:]

    def get_paused(self, sandbox_id: str) -> list[InterceptedWebhook]:
        return [c for c in self._captures.get(sandbox_id, []) if c.paused]

    def clear(self, sandbox_id: str) -> int:
        count = len(self._captures.get(sandbox_id, []))
        self._captures[sandbox_id] = []
        return count

    def remove_rule(self, sandbox_id: str, rule_id: str) -> bool:
        rules = self._rules.get(sandbox_id, [])
        for i, r in enumerate(rules):
            if r.rule_id == rule_id:
                rules.pop(i)
                return True
        return False
