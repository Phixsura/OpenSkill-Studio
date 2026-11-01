"""Sandbox Feature Gate — runtime feature gating for sandbox capabilities.

Controls access to sandbox capabilities (network, filesystem, IPC) based
on extension tier, admin overrides, and runtime conditions.
"""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum


class Tier(str, Enum):
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    ENTERPRISE = "enterprise"


TIER_HIERARCHY = {Tier.FREE: 0, Tier.STARTER: 1, Tier.PRO: 2, Tier.ENTERPRISE: 3}


@dataclass
class FeatureGate:
    feature: str
    min_tier: Tier
    description: str = ""
    enabled: bool = True


class SandboxFeatureGateService:
    """Controls sandbox capability access based on tiers and overrides."""

    def __init__(self):
        self._gates: dict[str, FeatureGate] = {}
        self._sandbox_tiers: dict[str, Tier] = {}
        self._overrides: dict[str, dict[str, bool]] = defaultdict(dict)

    def define_gate(self, feature: str, min_tier: Tier,
                    description: str = "") -> FeatureGate:
        gate = FeatureGate(feature=feature, min_tier=min_tier, description=description)
        self._gates[feature] = gate
        return gate

    def set_tier(self, sandbox_id: str, tier: Tier) -> None:
        self._sandbox_tiers[sandbox_id] = tier

    def set_override(self, sandbox_id: str, feature: str, enabled: bool) -> None:
        self._overrides[sandbox_id][feature] = enabled

    def clear_override(self, sandbox_id: str, feature: str) -> bool:
        return self._overrides.get(sandbox_id, {}).pop(feature, None) is not None

    def is_enabled(self, sandbox_id: str, feature: str) -> dict:
        gate = self._gates.get(feature)
        if not gate:
            return {"enabled": False, "reason": "Feature not defined"}
        if not gate.enabled:
            return {"enabled": False, "reason": "Feature globally disabled"}

        # Check override first
        override = self._overrides.get(sandbox_id, {}).get(feature)
        if override is not None:
            return {"enabled": override, "reason": "admin override"}

        # Check tier
        tier = self._sandbox_tiers.get(sandbox_id, Tier.FREE)
        tier_level = TIER_HIERARCHY[tier]
        min_level = TIER_HIERARCHY[gate.min_tier]

        if tier_level >= min_level:
            return {"enabled": True, "reason": f"tier {tier.value} >= {gate.min_tier.value}"}
        return {"enabled": False, "reason": f"Requires {gate.min_tier.value} tier (current: {tier.value})"}

    def get_available_features(self, sandbox_id: str) -> list[str]:
        return [f for f in self._gates if self.is_enabled(sandbox_id, f)["enabled"]]

    def get_all_gates(self) -> list[dict]:
        return [{"feature": g.feature, "min_tier": g.min_tier.value,
                 "enabled": g.enabled, "description": g.description}
                for g in self._gates.values()]

    def disable_gate(self, feature: str) -> bool:
        gate = self._gates.get(feature)
        if gate:
            gate.enabled = False
            return True
        return False

    def enable_gate(self, feature: str) -> bool:
        gate = self._gates.get(feature)
        if gate:
            gate.enabled = True
            return True
        return False
