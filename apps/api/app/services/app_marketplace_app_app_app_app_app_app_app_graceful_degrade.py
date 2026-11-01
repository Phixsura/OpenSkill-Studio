"""Graceful degradation controller — shed load under pressure."""
from __future__ import annotations


class GracefulDegradation:
    def __init__(self):
        self._features: dict[str, dict] = {}
        self._active_level = "full"

    def register_feature(self, name: str, priority: int, fallback: str = "disabled") -> dict:
        self._features[name] = {"name": name, "priority": priority,
                                 "fallback": fallback, "active": True}
        return self._features[name]

    def set_level(self, level: str) -> dict:
        self._active_level = level
        if level == "full":
            for f in self._features.values():
                f["active"] = True
        elif level == "reduced":
            for f in self._features.values():
                f["active"] = f["priority"] >= 5
        elif level == "minimal":
            for f in self._features.values():
                f["active"] = f["priority"] >= 8
        elif level == "emergency":
            for f in self._features.values():
                f["active"] = f["priority"] >= 10
        active_count = sum(1 for f in self._features.values() if f["active"])
        return {"level": level, "active_features": active_count, "total": len(self._features)}

    def is_active(self, name: str) -> bool:
        return self._features.get(name, {}).get("active", False)

    def status(self) -> dict:
        active = sum(1 for f in self._features.values() if f["active"])
        return {"level": self._active_level, "active": active,
                "total": len(self._features),
                "shed": len(self._features) - active}
