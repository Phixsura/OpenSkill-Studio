"""Feature usage analytics — track which features users actually use."""
from __future__ import annotations
from collections import defaultdict


class FeatureUsageTracker:
    def __init__(self):
        self._usage: dict[str, dict] = defaultdict(lambda: {"count": 0, "users": set()})

    def track(self, feature: str, user_id: str) -> dict:
        self._usage[feature]["count"] += 1
        self._usage[feature]["users"].add(user_id)
        return {"feature": feature, "tracked": True}

    def top_features(self, limit: int = 10) -> list[dict]:
        ranked = sorted(self._usage.items(), key=lambda x: -x[1]["count"])[:limit]
        return [{"feature": k, "count": v["count"], "unique_users": len(v["users"])} for k, v in ranked]

    def unused_features(self, all_features: list[str]) -> list[str]:
        used = set(self._usage.keys())
        return sorted(set(all_features) - used)

    def stats(self) -> dict:
        total_events = sum(v["count"] for v in self._usage.values())
        return {"features_used": len(self._usage), "total_events": total_events}
