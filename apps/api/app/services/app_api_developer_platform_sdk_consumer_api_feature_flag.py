"""Endpoint Feature Flag — per-endpoint feature toggles with rollout percentage."""
from __future__ import annotations

import hashlib
import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class FeatureFlag:
    flag_id: str
    name: str
    description: str = ""
    enabled: bool = False
    rollout_pct: float = 0.0  # 0-100
    allowlist: list[str] = field(default_factory=list)
    denylist: list[str] = field(default_factory=list)


@dataclass
class FeatureFlagManager:
    """Manage per-endpoint feature flags with gradual rollout."""

    _flags: dict[str, FeatureFlag] = field(default_factory=dict)
    _evaluations: list[dict] = field(default_factory=list)

    def create_flag(self, flag: FeatureFlag) -> dict:
        if flag.flag_id in self._flags:
            raise ValueError(f"Flag {flag.flag_id} already exists")
        if not 0 <= flag.rollout_pct <= 100:
            raise ValueError("rollout_pct must be between 0 and 100")
        self._flags[flag.flag_id] = flag
        logger.info("flag_created", flag_id=flag.flag_id, name=flag.name)
        return {"flag_id": flag.flag_id, "enabled": flag.enabled}

    def evaluate(self, flag_id: str, consumer_id: str) -> dict:
        flag = self._flags.get(flag_id)
        if not flag:
            return {"flag_id": flag_id, "active": False, "reason": "not_found"}
        if not flag.enabled:
            result = {"flag_id": flag_id, "active": False, "reason": "disabled"}
        elif consumer_id in flag.denylist:
            result = {"flag_id": flag_id, "active": False, "reason": "denylisted"}
        elif consumer_id in flag.allowlist:
            result = {"flag_id": flag_id, "active": True, "reason": "allowlisted"}
        elif flag.rollout_pct >= 100:
            result = {"flag_id": flag_id, "active": True, "reason": "full_rollout"}
        elif flag.rollout_pct <= 0:
            result = {"flag_id": flag_id, "active": False, "reason": "zero_rollout"}
        else:
            # Deterministic hash-based rollout
            h = hashlib.md5(f"{flag_id}:{consumer_id}".encode()).hexdigest()
            bucket = int(h[:8], 16) % 100
            active = bucket < flag.rollout_pct
            result = {"flag_id": flag_id, "active": active,
                      "reason": "rollout", "bucket": bucket}
        self._evaluations.append({**result, "consumer_id": consumer_id})
        return result

    def toggle(self, flag_id: str, enabled: bool) -> dict:
        flag = self._flags.get(flag_id)
        if not flag:
            raise ValueError(f"Flag {flag_id} not found")
        flag.enabled = enabled
        logger.info("flag_toggled", flag_id=flag_id, enabled=enabled)
        return {"flag_id": flag_id, "enabled": enabled}

    def set_rollout(self, flag_id: str, pct: float) -> dict:
        flag = self._flags.get(flag_id)
        if not flag:
            raise ValueError(f"Flag {flag_id} not found")
        if not 0 <= pct <= 100:
            raise ValueError("Percentage must be between 0 and 100")
        flag.rollout_pct = pct
        return {"flag_id": flag_id, "rollout_pct": pct}

    def add_to_allowlist(self, flag_id: str, consumer_id: str) -> dict:
        flag = self._flags.get(flag_id)
        if not flag:
            raise ValueError(f"Flag {flag_id} not found")
        if consumer_id not in flag.allowlist:
            flag.allowlist.append(consumer_id)
        return {"flag_id": flag_id, "allowlist_size": len(flag.allowlist)}

    def list_flags(self) -> list[dict]:
        return [
            {"flag_id": f.flag_id, "name": f.name, "enabled": f.enabled,
             "rollout_pct": f.rollout_pct, "allowlist_size": len(f.allowlist)}
            for f in self._flags.values()
        ]

    def get_stats(self, flag_id: str) -> dict:
        evals = [e for e in self._evaluations if e["flag_id"] == flag_id]
        active = sum(1 for e in evals if e["active"])
        return {
            "flag_id": flag_id,
            "total_evaluations": len(evals),
            "active_count": active,
            "inactive_count": len(evals) - active,
            "activation_rate": round(active / len(evals) * 100, 1) if evals else 0,
        }
