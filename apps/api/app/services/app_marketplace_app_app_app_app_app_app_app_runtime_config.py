"""Platform runtime configuration — dynamic runtime config with hot reload."""
from __future__ import annotations
import time
import hashlib


class RuntimeConfig:
    def __init__(self):
        self._config: dict[str, dict] = {}
        self._history: list[dict] = []

    def set(self, key: str, value: str, env: str = "production", changed_by: str = "system") -> dict:
        prev = self._config.get(key, {}).get("value")
        version = hashlib.sha256(f"{key}:{value}:{time.time()}".encode()).hexdigest()[:12]
        self._config[key] = {"value": value, "env": env, "version": version,
                              "updated_at": time.time(), "changed_by": changed_by}
        self._history.append({"key": key, "old": prev, "new": value,
                               "version": version, "changed_by": changed_by})
        return {"key": key, "version": version, "applied": True}

    def get(self, key: str, default: str = "") -> dict:
        entry = self._config.get(key)
        if not entry:
            return {"key": key, "value": default, "found": False}
        return {"key": key, "value": entry["value"], "found": True,
                "version": entry["version"], "env": entry["env"]}

    def get_all(self, env: str = "") -> dict:
        if env:
            filtered = {k: v for k, v in self._config.items() if v["env"] == env}
        else:
            filtered = dict(self._config)
        return {"count": len(filtered),
                "keys": sorted(filtered.keys()),
                "configs": {k: v["value"] for k, v in filtered.items()}}

    def diff(self, env1: str, env2: str) -> dict:
        c1 = {k: v["value"] for k, v in self._config.items() if v["env"] == env1}
        c2 = {k: v["value"] for k, v in self._config.items() if v["env"] == env2}
        only_env1 = sorted(set(c1) - set(c2))
        only_env2 = sorted(set(c2) - set(c1))
        different = []
        for k in sorted(set(c1) & set(c2)):
            if c1[k] != c2[k]:
                different.append({"key": k, env1: c1[k], env2: c2[k]})
        return {"only_in_" + env1: only_env1, "only_in_" + env2: only_env2,
                "different": different, "total_diffs": len(only_env1) + len(only_env2) + len(different)}

    def audit_log(self, limit: int = 20) -> list[dict]:
        return self._history[-limit:]

    def rollback(self, key: str) -> dict:
        changes = [h for h in self._history if h["key"] == key and h["old"] is not None]
        if not changes:
            return {"key": key, "rolled_back": False, "reason": "no_previous_value"}
        prev_value = changes[-1]["old"]
        return self.set(key, prev_value, changed_by="rollback")
