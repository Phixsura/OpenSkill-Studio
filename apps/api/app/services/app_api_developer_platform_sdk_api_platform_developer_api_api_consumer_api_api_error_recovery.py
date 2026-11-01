"""API Consumer Error Recovery — automated error recovery strategies."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import structlog

log = structlog.get_logger()

class RecoveryAction(str, Enum):
    RETRY = "retry"
    FALLBACK = "fallback"
    CIRCUIT_BREAK = "circuit_break"
    ESCALATE = "escalate"
    IGNORE = "ignore"

@dataclass
class RecoveryRule:
    rule_id: str
    error_pattern: str  # status code range or error type
    action: RecoveryAction
    max_attempts: int = 3
    fallback_endpoint: str = ""

@dataclass
class RecoveryEvent:
    event_id: str
    consumer_id: str
    error_code: int
    action_taken: RecoveryAction
    success: bool
    attempts: int = 1

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiErrorRecovery:
    def __init__(self) -> None:
        self._rules: dict[tuple[str, str], list[RecoveryRule]] = {}
        self._events: dict[str, list[RecoveryEvent]] = {}

    def add_rule(self, installation_id: str, consumer_id: str, rule: RecoveryRule) -> RecoveryRule:
        if not installation_id: raise ValueError("installation_id is required")
        self._rules.setdefault((installation_id, consumer_id), []).append(rule)
        return rule

    def get_action(self, installation_id: str, consumer_id: str, error_code: int) -> RecoveryAction:
        rules = self._rules.get((installation_id, consumer_id), [])
        for r in rules:
            if r.error_pattern == str(error_code) or r.error_pattern == f"{error_code // 100}xx":
                return r.action
        if error_code >= 500: return RecoveryAction.RETRY
        if error_code == 429: return RecoveryAction.CIRCUIT_BREAK
        return RecoveryAction.ESCALATE

    def record_recovery(self, installation_id: str, event: RecoveryEvent) -> RecoveryEvent:
        self._events.setdefault(installation_id, []).append(event)
        return event

    def recovery_rate(self, installation_id: str) -> float:
        events = self._events.get(installation_id, [])
        if not events: return 0.0
        return round(sum(1 for e in events if e.success) / len(events) * 100, 1)

    def list_rules(self, installation_id: str, consumer_id: str) -> list[RecoveryRule]:
        return self._rules.get((installation_id, consumer_id), [])
