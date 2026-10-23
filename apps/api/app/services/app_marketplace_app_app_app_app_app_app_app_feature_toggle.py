"""Feature toggle router — route traffic to features based on user segments."""
from __future__ import annotations
import hashlib


class FeatureToggleRouter:
    def __init__(self):
        self._toggles: dict[str, dict] = {}

    def create(self, key: str, *, enabled: bool = False,
               rollout_pct: int = 0, segments: list[str] | None = None) -> dict:
        self._toggles[key] = {"key": key, "enabled": enabled,
                               "rollout_pct": rollout_pct, "segments": segments or []}
        return {"key": key, "enabled": enabled, "rollout_pct": rollout_pct}

    def evaluate(self, key: str, *, user_id: str = "", segment: str = "") -> dict:
        t = self._toggles.get(key)
        if not t:
            return {"enabled": False, "reason": "toggle_not_found"}
        if not t["enabled"]:
            return {"enabled": False, "reason": "globally_disabled"}
        if t["segments"] and segment in t["segments"]:
            return {"enabled": True, "reason": "segment_match"}
        if t["rollout_pct"] > 0 and user_id:
            h = int(hashlib.md5(f"{key}:{user_id}".encode()).hexdigest()[:8], 16)
            bucket = h % 100
            if bucket < t["rollout_pct"]:
                return {"enabled": True, "reason": "rollout", "bucket": bucket}
        if t["rollout_pct"] == 100:
            return {"enabled": True, "reason": "full_rollout"}
        return {"enabled": False, "reason": "not_in_rollout"}

    def list_toggles(self) -> list[dict]:
        return list(self._toggles.values())
