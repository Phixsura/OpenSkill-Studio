"""Feature Flag Evaluator — per-tenant/user flag evaluation for progressive app rollouts.

Provides feature gating for the developer platform:
- Boolean, percentage, and user-list targeting
- Tenant-scoped flags (org-level overrides)
- Sticky bucketing via deterministic hashing
- Flag dependency chains (flag A requires flag B)
- Default fallback values
- Evaluation audit trail
- Bulk evaluation for rendering
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum

import structlog

log = structlog.get_logger()


class FlagType(str, Enum):
    BOOLEAN = "boolean"
    PERCENTAGE = "percentage"
    USER_LIST = "user_list"
    TENANT_LIST = "tenant_list"


class FlagStatus(str, Enum):
    ACTIVE = "active"
    DISABLED = "disabled"
    ARCHIVED = "archived"


@dataclass
class FlagRule:
    """A single targeting rule within a flag."""

    rule_type: FlagType
    value: bool | int | list[str] = True
    # For percentage: 0-100 integer
    # For user_list/tenant_list: list of IDs


@dataclass
class FeatureFlag:
    """A feature flag definition."""

    key: str
    description: str
    status: FlagStatus = FlagStatus.ACTIVE
    default_value: bool = False
    rules: list[FlagRule] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)  # other flag keys
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class EvalContext:
    """Context for evaluating a flag."""

    user_id: str | None = None
    tenant_id: str | None = None
    attributes: dict[str, str] = field(default_factory=dict)


@dataclass
class EvalResult:
    """Result of evaluating a single flag."""

    key: str
    enabled: bool
    reason: str
    rule_index: int | None = None


def _deterministic_bucket(flag_key: str, entity_id: str) -> int:
    """Deterministic 0-99 bucket for sticky percentage rollouts.

    Same (flag, entity) always maps to the same bucket.
    """
    raw = f"{flag_key}:{entity_id}"
    h = hashlib.sha256(raw.encode()).hexdigest()
    return int(h[:8], 16) % 100


class FeatureFlagEvaluator:
    """Evaluate feature flags against user/tenant context."""

    def __init__(self):
        self._flags: dict[str, FeatureFlag] = {}
        self._overrides: dict[tuple[str, str], bool] = {}  # (flag_key, tenant_id) → bool
        self._eval_log: list[EvalResult] = []

    # ── Flag management ──────────────────────────────────

    def register(self, flag: FeatureFlag) -> None:
        self._flags[flag.key] = flag

    def get(self, key: str) -> FeatureFlag | None:
        return self._flags.get(key)

    def list_flags(self, status: FlagStatus | None = None) -> list[FeatureFlag]:
        flags = list(self._flags.values())
        if status:
            flags = [f for f in flags if f.status == status]
        return sorted(flags, key=lambda f: f.key)

    def set_override(self, flag_key: str, tenant_id: str, value: bool) -> None:
        """Set a tenant-level override for a flag."""
        self._overrides[(flag_key, tenant_id)] = value

    def remove_override(self, flag_key: str, tenant_id: str) -> None:
        self._overrides.pop((flag_key, tenant_id), None)

    # ── Evaluation ───────────────────────────────────────

    def evaluate(self, key: str, ctx: EvalContext) -> EvalResult:
        """Evaluate a single flag for the given context."""
        flag = self._flags.get(key)

        if flag is None:
            result = EvalResult(key=key, enabled=False, reason="flag_not_found")
            self._eval_log.append(result)
            return result

        if flag.status != FlagStatus.ACTIVE:
            result = EvalResult(key=key, enabled=flag.default_value,
                                reason=f"flag_{flag.status.value}")
            self._eval_log.append(result)
            return result

        # Check tenant override
        if ctx.tenant_id:
            override = self._overrides.get((key, ctx.tenant_id))
            if override is not None:
                result = EvalResult(key=key, enabled=override, reason="tenant_override")
                self._eval_log.append(result)
                return result

        # Check dependency chain
        for dep_key in flag.depends_on:
            dep_result = self.evaluate(dep_key, ctx)
            if not dep_result.enabled:
                result = EvalResult(key=key, enabled=False,
                                    reason=f"dependency_not_met:{dep_key}")
                self._eval_log.append(result)
                return result

        # Evaluate rules in order (first match wins)
        for i, rule in enumerate(flag.rules):
            match = self._evaluate_rule(rule, key, ctx)
            if match is not None:
                result = EvalResult(key=key, enabled=match, reason=f"rule_{i}",
                                    rule_index=i)
                self._eval_log.append(result)
                return result

        # No rule matched → default
        result = EvalResult(key=key, enabled=flag.default_value, reason="default")
        self._eval_log.append(result)
        return result

    def evaluate_bulk(self, keys: list[str], ctx: EvalContext) -> dict[str, bool]:
        """Evaluate multiple flags at once. Returns key → enabled map."""
        return {key: self.evaluate(key, ctx).enabled for key in keys}

    def is_enabled(self, key: str, ctx: EvalContext) -> bool:
        """Shorthand: returns just the boolean."""
        return self.evaluate(key, ctx).enabled

    # ── Audit ────────────────────────────────────────────

    def get_eval_log(self, limit: int = 50) -> list[EvalResult]:
        return self._eval_log[-limit:]

    def clear_eval_log(self) -> None:
        self._eval_log.clear()

    # ── Internals ────────────────────────────────────────

    def _evaluate_rule(self, rule: FlagRule, flag_key: str,
                       ctx: EvalContext) -> bool | None:
        """Evaluate a single rule. Returns True/False if matched, None if not applicable."""
        if rule.rule_type == FlagType.BOOLEAN:
            return bool(rule.value)

        elif rule.rule_type == FlagType.PERCENTAGE:
            pct = int(rule.value) if isinstance(rule.value, (int, float)) else 0
            entity = ctx.user_id or ctx.tenant_id or "anonymous"
            bucket = _deterministic_bucket(flag_key, entity)
            return bucket < pct

        elif rule.rule_type == FlagType.USER_LIST:
            if ctx.user_id and isinstance(rule.value, list):
                return ctx.user_id in rule.value
            return None

        elif rule.rule_type == FlagType.TENANT_LIST:
            if ctx.tenant_id and isinstance(rule.value, list):
                return ctx.tenant_id in rule.value
            return None

        return None
