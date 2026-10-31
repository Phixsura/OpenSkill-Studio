"""App Feature Usage — track which features users actually use.

Tracks feature adoption and usage frequency:
- Record feature usage events
- Compute adoption rate (% of users using a feature)
- Usage frequency per feature
- Per-installation scoped tracking
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class FeatureUsageStats:
    """Usage statistics for a feature."""

    feature_id: str
    unique_users: int
    total_uses: int
    adoption_pct: float
    last_used_at: float


class AppFeatureUsage:
    """Track which features users actually use."""

    def __init__(self) -> None:
        # (installation_id, feature_id) → {user_id: use_count}
        self._usage: dict[tuple[str, str], dict[str, int]] = {}
        # (installation_id, feature_id) → last_used_at
        self._last_used: dict[tuple[str, str], float] = {}
        # installation_id → set of all known user_ids
        self._users: dict[str, set[str]] = {}

    def record_usage(
        self,
        installation_id: str,
        feature_id: str,
        user_id: str,
        now: float | None = None,
    ) -> None:
        """Record a feature usage event."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if not feature_id:
            raise ValueError("feature_id is required")
        if not user_id:
            raise ValueError("user_id is required")

        key = (installation_id, feature_id)
        users = self._usage.setdefault(key, {})
        users[user_id] = users.get(user_id, 0) + 1
        self._last_used[key] = now or time.time()
        self._users.setdefault(installation_id, set()).add(user_id)

    def get_stats(
        self, installation_id: str, feature_id: str
    ) -> FeatureUsageStats:
        """Get usage stats for a feature."""
        key = (installation_id, feature_id)
        users = self._usage.get(key, {})
        total_users = len(self._users.get(installation_id, set()))
        unique = len(users)
        total = sum(users.values())
        adoption = round(unique / total_users * 100, 1) if total_users > 0 else 0.0

        return FeatureUsageStats(
            feature_id=feature_id,
            unique_users=unique,
            total_uses=total,
            adoption_pct=adoption,
            last_used_at=self._last_used.get(key, 0),
        )

    def get_all_stats(self, installation_id: str) -> list[FeatureUsageStats]:
        """Get stats for all features, sorted by adoption."""
        features = {
            fid for (inst, fid) in self._usage if inst == installation_id
        }
        stats = [self.get_stats(installation_id, fid) for fid in features]
        return sorted(stats, key=lambda s: s.adoption_pct, reverse=True)

    def most_used(self, installation_id: str, limit: int = 10) -> list[FeatureUsageStats]:
        """Get most-used features by total uses."""
        stats = self.get_all_stats(installation_id)
        return sorted(stats, key=lambda s: s.total_uses, reverse=True)[:limit]

    def least_adopted(self, installation_id: str, limit: int = 10) -> list[FeatureUsageStats]:
        """Get least-adopted features."""
        stats = self.get_all_stats(installation_id)
        return sorted(stats, key=lambda s: s.adoption_pct)[:limit]
