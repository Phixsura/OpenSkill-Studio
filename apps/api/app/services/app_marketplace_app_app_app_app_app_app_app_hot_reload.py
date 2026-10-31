"""Config hot reload — reload configuration without service restart."""
from __future__ import annotations
import hashlib


class HotReloadManager:
    def __init__(self):
        self._configs: dict[str, dict] = {}
        self._reload_count = 0

    def register(self, name: str, config: dict) -> dict:
        config_hash = hashlib.sha256(str(sorted(config.items())).encode()).hexdigest()[:12]
        self._configs[name] = {"config": config, "hash": config_hash, "version": 1}
        return {"name": name, "hash": config_hash}

    def check_update(self, name: str, new_config: dict) -> dict:
        new_hash = hashlib.sha256(str(sorted(new_config.items())).encode()).hexdigest()[:12]
        current = self._configs.get(name)
        if not current:
            return {"changed": False, "reason": "not_registered"}
        changed = current["hash"] != new_hash
        if changed:
            current["config"] = new_config
            current["hash"] = new_hash
            current["version"] += 1
            self._reload_count += 1
        return {"name": name, "changed": changed, "version": current["version"],
                "hash": new_hash}

    def stats(self) -> dict:
        return {"configs": len(self._configs), "total_reloads": self._reload_count}
