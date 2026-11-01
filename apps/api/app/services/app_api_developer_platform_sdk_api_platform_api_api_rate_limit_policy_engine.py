"""App API Developer Rate Limit Policy Engine — configurable multi-rule rate limiting."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class RateLimitPolicy:
    policy_id: str
    name: str
    rules: list[dict] = field(default_factory=list)  # [{endpoint, method, limit, window_seconds}]
    applied_to: list[str] = field(default_factory=list)  # consumer_ids
    enforcement: str = "enforce"  # "enforce", "monitor", "disabled"

class AppAPIDeveloperPlatformSDKApiPlatformApiApiRateLimitPolicyEngine:
    def __init__(self) -> None:
        self._policies: dict[tuple[str, str], RateLimitPolicy] = {}

    def create(self, installation_id: str, policy_id: str, name: str, rules: list[dict], enforcement: str = "enforce") -> RateLimitPolicy:
        if not installation_id: raise ValueError("installation_id is required")
        if enforcement not in ("enforce", "monitor", "disabled"): raise ValueError("invalid enforcement")
        if not rules: raise ValueError("at least one rule required")
        key = (installation_id, policy_id)
        if key in self._policies: raise ValueError(f"Policy {policy_id} exists")
        p = RateLimitPolicy(policy_id=policy_id, name=name, rules=rules, enforcement=enforcement)
        self._policies[key] = p
        return p

    def apply_to(self, installation_id: str, policy_id: str, consumer_ids: list[str]) -> RateLimitPolicy:
        key = (installation_id, policy_id)
        p = self._policies.get(key)
        if p is None: raise KeyError(f"Policy {policy_id} not found")
        for cid in consumer_ids:
            if cid not in p.applied_to: p.applied_to.append(cid)
        return p

    def active_policies(self, installation_id: str) -> list[RateLimitPolicy]:
        return [p for (inst, _), p in self._policies.items() if inst == installation_id and p.enforcement != "disabled"]

    def policy_for_consumer(self, installation_id: str, consumer_id: str) -> list[RateLimitPolicy]:
        return [p for (inst, _), p in self._policies.items() if inst == installation_id and consumer_id in p.applied_to and p.enforcement == "enforce"]

    def all_policies(self, installation_id: str) -> list[RateLimitPolicy]:
        return [p for (inst, _), p in self._policies.items() if inst == installation_id]
