"""Config sync manager — sync configuration across services and environments."""
from __future__ import annotations


class ConfigSyncManager:
    def __init__(self):
        self._configs: dict[str, dict[str, str]] = {}  # env -> key-value

    def set_config(self, env: str, key: str, value: str) -> dict:
        self._configs.setdefault(env, {})[key] = value
        return {"env": env, "key": key, "set": True}

    def sync(self, source_env: str, target_env: str, keys: list[str] | None = None) -> dict:
        src = self._configs.get(source_env, {})
        self._configs.setdefault(target_env, {})
        synced = 0
        for k, v in src.items():
            if keys and k not in keys:
                continue
            self._configs[target_env][k] = v
            synced += 1
        return {"source": source_env, "target": target_env, "synced": synced}

    def diff(self, env1: str, env2: str) -> dict:
        c1 = self._configs.get(env1, {})
        c2 = self._configs.get(env2, {})
        only1 = sorted(set(c1) - set(c2))
        only2 = sorted(set(c2) - set(c1))
        different = [k for k in sorted(set(c1) & set(c2)) if c1[k] != c2[k]]
        return {"only_in_" + env1: only1, "only_in_" + env2: only2,
                "different": different, "in_sync": not (only1 or only2 or different)}

    def stats(self) -> dict:
        return {"environments": len(self._configs),
                "total_keys": sum(len(v) for v in self._configs.values())}
