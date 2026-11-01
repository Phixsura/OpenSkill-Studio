"""Platform feature registry — centralized feature flag management."""
from __future__ import annotations


class FeatureRegistry:
    def __init__(self):
        self._features: dict[str, dict] = {}

    def register(self, name: str, enabled: bool = False, description: str = "",
                 owner: str = "", tags: list[str] | None = None) -> dict:
        self._features[name] = {"name": name, "enabled": enabled,
                                 "description": description, "owner": owner,
                                 "tags": tags or []}
        return self._features[name]

    def enable(self, name: str) -> dict:
        self._features[name]["enabled"] = True
        return {"name": name, "enabled": True}

    def disable(self, name: str) -> dict:
        self._features[name]["enabled"] = False
        return {"name": name, "enabled": False}

    def is_enabled(self, name: str) -> bool:
        return self._features.get(name, {}).get("enabled", False)

    def list_features(self, tag: str = "", enabled_only: bool = False) -> list[dict]:
        results = list(self._features.values())
        if tag:
            results = [f for f in results if tag in f["tags"]]
        if enabled_only:
            results = [f for f in results if f["enabled"]]
        return sorted(results, key=lambda f: f["name"])

    def stats(self) -> dict:
        enabled = sum(1 for f in self._features.values() if f["enabled"])
        return {"total": len(self._features), "enabled": enabled,
                "disabled": len(self._features) - enabled}
