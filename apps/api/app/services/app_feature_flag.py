"""App Feature Flag Manager — toggle features per installation with rollout rules.

Manages feature flags for installed apps:
- Boolean on/off flags per installation
- Percentage-based rollout (hash-stable)
- Override lists (force enable/disable per user)
- Default values for unknown flags
- Audit trail of flag changes
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class FlagConfig:
    """Configuration for a feature flag."""

    flag_id: str
    enabled: bool = False
    rollout_pct: float = 0.0  # 0-100, 0 = off, 100 = all
    force_enable: list[str] = field(default_factory=list)   # user IDs
    force_disable: list[str] = field(default_factory=list)  # user IDs
    description: str = ""
    updated_at: float = field(default_factory=time.time)


@dataclass
class FlagEvaluation:
    """Result of evaluating a flag for a user."""

    flag_id: str
    enabled: bool
    reason: str  # "default", "global", "rollout", "force_enable", "force_disable"


@dataclass
class FlagChange:
    """Audit record for a flag change."""

    flag_id: str
    installation_id: str
    field: str
    old_value: object
    new_value: object
    timestamp: float = field(default_factory=time.time)


def _hash_user_pct(flag_id: str, user_id: str) -> float:
    """Deterministic hash to 0-100 for rollout bucketing."""
    h = hashlib.sha256(f"{flag_id}:{user_id}".encode()).hexdigest()
    return (int(h[:8], 16) % 10000) / 100.0


class AppFeatureFlagManager:
    """Manage feature flags per installation."""

    def __init__(self) -> None:
        # (installation_id, flag_id) → FlagConfig
        self._flags: dict[tuple[str, str], FlagConfig] = {}
        self._changes: list[FlagChange] = []

    def create_flag(
        self,
        installation_id: str,
        flag_id: str,
        enabled: bool = False,
        rollout_pct: float = 0.0,
        description: str = "",
    ) -> FlagConfig:
        """Create a new feature flag."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if not flag_id:
            raise ValueError("flag_id is required")
        if not 0 <= rollout_pct <= 100:
            raise ValueError("rollout_pct must be 0-100")

        key = (installation_id, flag_id)
        if key in self._flags:
            raise ValueError(f"Flag {flag_id} already exists")

        config = FlagConfig(
            flag_id=flag_id,
            enabled=enabled,
            rollout_pct=rollout_pct,
            description=description,
        )
        self._flags[key] = config
        return config

    def evaluate(
        self,
        installation_id: str,
        flag_id: str,
        user_id: str = "",
    ) -> FlagEvaluation:
        """Evaluate a flag for a specific user."""
        key = (installation_id, flag_id)
        config = self._flags.get(key)

        if config is None:
            return FlagEvaluation(flag_id=flag_id, enabled=False, reason="default")

        # Force overrides first
        if user_id and user_id in config.force_disable:
            return FlagEvaluation(flag_id=flag_id, enabled=False, reason="force_disable")
        if user_id and user_id in config.force_enable:
            return FlagEvaluation(flag_id=flag_id, enabled=True, reason="force_enable")

        # Global off
        if not config.enabled:
            return FlagEvaluation(flag_id=flag_id, enabled=False, reason="global")

        # Percentage rollout
        if config.rollout_pct >= 100:
            return FlagEvaluation(flag_id=flag_id, enabled=True, reason="rollout")
        if config.rollout_pct > 0 and user_id:
            bucket = _hash_user_pct(flag_id, user_id)
            if bucket < config.rollout_pct:
                return FlagEvaluation(flag_id=flag_id, enabled=True, reason="rollout")
            return FlagEvaluation(flag_id=flag_id, enabled=False, reason="rollout")

        # Enabled globally with 0% rollout = full on
        return FlagEvaluation(flag_id=flag_id, enabled=True, reason="global")

    def toggle(self, installation_id: str, flag_id: str, enabled: bool) -> FlagConfig:
        """Toggle a flag on/off."""
        config = self._get(installation_id, flag_id)
        old = config.enabled
        config.enabled = enabled
        config.updated_at = time.time()
        self._changes.append(FlagChange(
            flag_id=flag_id, installation_id=installation_id,
            field="enabled", old_value=old, new_value=enabled))
        return config

    def set_rollout(self, installation_id: str, flag_id: str, pct: float) -> FlagConfig:
        """Set rollout percentage."""
        if not 0 <= pct <= 100:
            raise ValueError("rollout_pct must be 0-100")
        config = self._get(installation_id, flag_id)
        old = config.rollout_pct
        config.rollout_pct = pct
        config.updated_at = time.time()
        self._changes.append(FlagChange(
            flag_id=flag_id, installation_id=installation_id,
            field="rollout_pct", old_value=old, new_value=pct))
        return config

    def add_override(
        self, installation_id: str, flag_id: str, user_id: str, enable: bool
    ) -> None:
        """Add a user-level override."""
        config = self._get(installation_id, flag_id)
        if enable:
            if user_id not in config.force_enable:
                config.force_enable.append(user_id)
            # Remove from disable if present
            config.force_disable = [u for u in config.force_disable if u != user_id]
        else:
            if user_id not in config.force_disable:
                config.force_disable.append(user_id)
            config.force_enable = [u for u in config.force_enable if u != user_id]

    def list_flags(self, installation_id: str) -> list[FlagConfig]:
        return [
            config for (inst, _), config in self._flags.items()
            if inst == installation_id
        ]

    def get_changes(self, installation_id: str, flag_id: str | None = None, limit: int = 50) -> list[FlagChange]:
        if not installation_id:
            raise ValueError("installation_id is required")
        records = [c for c in self._changes if c.installation_id == installation_id]
        if flag_id:
            records = [c for c in records if c.flag_id == flag_id]
        return list(reversed(records[-limit:]))

    def _get(self, installation_id: str, flag_id: str) -> FlagConfig:
        key = (installation_id, flag_id)
        config = self._flags.get(key)
        if config is None:
            raise KeyError(f"Flag {flag_id} not found")
        return config
