"""Usage Limiter — enforce per-extension usage limits with sliding windows.

Tracks API calls, storage, and compute per extension per org with
configurable sliding windows and soft/hard limit enforcement.
"""
from __future__ import annotations
import time
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class UsageWindow:
    window_seconds: float
    hard_limit: int
    soft_limit: int  # triggers warning
    timestamps: list[float] = None

    def __post_init__(self):
        if self.timestamps is None:
            self.timestamps = []

    def _clean(self) -> None:
        cutoff = time.monotonic() - self.window_seconds
        self.timestamps = [t for t in self.timestamps if t > cutoff]

    def record(self) -> None:
        self.timestamps.append(time.monotonic())

    @property
    def count(self) -> int:
        self._clean()
        return len(self.timestamps)

    @property
    def exceeded_hard(self) -> bool:
        return self.count >= self.hard_limit

    @property
    def exceeded_soft(self) -> bool:
        return self.count >= self.soft_limit


class UsageLimiter:
    """Enforces per-extension usage limits with sliding windows."""

    def __init__(self):
        self._windows: dict[str, dict[str, UsageWindow]] = defaultdict(dict)

    def _key(self, extension_id: str, org_id: str) -> str:
        return f"{extension_id}:{org_id}"

    def configure(self, extension_id: str, org_id: str, metric: str,
                  window_seconds: float, hard_limit: int, soft_limit: int) -> None:
        key = self._key(extension_id, org_id)
        self._windows[key][metric] = UsageWindow(window_seconds, hard_limit, soft_limit)

    def check(self, extension_id: str, org_id: str, metric: str) -> dict:
        """Check if usage is allowed."""
        key = self._key(extension_id, org_id)
        window = self._windows.get(key, {}).get(metric)
        if not window:
            return {"allowed": True, "reason": "no_limit"}

        if window.exceeded_hard:
            return {"allowed": False, "reason": "hard_limit", "current": window.count,
                    "limit": window.hard_limit}

        warning = window.exceeded_soft
        return {"allowed": True, "warning": warning, "current": window.count,
                "soft_limit": window.soft_limit, "hard_limit": window.hard_limit}

    def record(self, extension_id: str, org_id: str, metric: str) -> dict:
        """Record usage and return status."""
        key = self._key(extension_id, org_id)
        window = self._windows.get(key, {}).get(metric)
        if not window:
            return {"recorded": True, "limited": False}

        if window.exceeded_hard:
            return {"recorded": False, "limited": True, "current": window.count}

        window.record()
        return {"recorded": True, "limited": False, "current": window.count,
                "warning": window.exceeded_soft}

    def get_usage(self, extension_id: str, org_id: str) -> dict:
        """Get all usage metrics for an extension+org."""
        key = self._key(extension_id, org_id)
        metrics = {}
        for metric, window in self._windows.get(key, {}).items():
            metrics[metric] = {
                "current": window.count,
                "soft_limit": window.soft_limit,
                "hard_limit": window.hard_limit,
                "percent": round(window.count / max(1, window.hard_limit) * 100, 1),
            }
        return {"extension_id": extension_id, "org_id": org_id, "metrics": metrics}

    def reset(self, extension_id: str, org_id: str, metric: str | None = None) -> bool:
        key = self._key(extension_id, org_id)
        windows = self._windows.get(key, {})
        if metric:
            w = windows.get(metric)
            if w:
                w.timestamps = []
                return True
            return False
        for w in windows.values():
            w.timestamps = []
        return bool(windows)
