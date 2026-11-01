"""Rollout Rules — declarative rules engine for extension feature rollouts.

Define rules for who sees what features based on org properties,
user attributes, percentages, and date ranges.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib


@dataclass
class RolloutRule:
    rule_id: str
    feature: str
    enabled: bool = True
    percentage: int = 100  # 0-100
    org_allowlist: list[str] = field(default_factory=list)
    org_blocklist: list[str] = field(default_factory=list)
    start_date: str = ""  # ISO date, empty = immediate
    end_date: str = ""    # ISO date, empty = no end
    min_plan: str = ""    # minimum plan tier required
    description: str = ""


class RolloutRulesEngine:
    """Evaluates rollout rules to determine feature availability."""

    def __init__(self):
        self._rules: dict[str, list[RolloutRule]] = {}

    def add_rule(self, rule: RolloutRule) -> None:
        self._rules.setdefault(rule.feature, []).append(rule)

    def remove_rule(self, feature: str, rule_id: str) -> bool:
        rules = self._rules.get(feature, [])
        before = len(rules)
        self._rules[feature] = [r for r in rules if r.rule_id != rule_id]
        return len(self._rules[feature]) < before

    def evaluate(self, feature: str, org_id: str, user_id: str = "",
                 plan: str = "", now: str = "") -> dict:
        """Evaluate if a feature is enabled for given context."""
        rules = self._rules.get(feature, [])
        if not rules:
            return {"enabled": False, "reason": "no_rules"}

        if not now:
            now = datetime.now(timezone.utc).isoformat()[:10]

        for rule in rules:
            if not rule.enabled:
                continue

            # Date range check
            if rule.start_date and now < rule.start_date:
                continue
            if rule.end_date and now > rule.end_date:
                continue

            # Blocklist
            if org_id in rule.org_blocklist:
                return {"enabled": False, "reason": "blocklisted", "rule_id": rule.rule_id}

            # Allowlist override
            if rule.org_allowlist and org_id in rule.org_allowlist:
                return {"enabled": True, "reason": "allowlisted", "rule_id": rule.rule_id}

            # Plan check
            if rule.min_plan:
                plan_order = {"free": 0, "starter": 1, "pro": 2, "enterprise": 3}
                if plan_order.get(plan, 0) < plan_order.get(rule.min_plan, 0):
                    continue

            # Percentage rollout
            if rule.percentage < 100:
                key = f"{feature}:{org_id}:{user_id or org_id}"
                bucket = int(hashlib.md5(key.encode()).hexdigest(), 16) % 100
                if bucket >= rule.percentage:
                    continue

            return {"enabled": True, "reason": "rule_matched", "rule_id": rule.rule_id}

        return {"enabled": False, "reason": "no_matching_rule"}

    def get_rules(self, feature: str) -> list[RolloutRule]:
        return list(self._rules.get(feature, []))

    def list_features(self) -> list[str]:
        return sorted(self._rules.keys())

    def bulk_evaluate(self, features: list[str], org_id: str,
                      user_id: str = "", plan: str = "") -> dict[str, bool]:
        """Evaluate multiple features at once."""
        return {f: self.evaluate(f, org_id, user_id, plan)["enabled"] for f in features}
