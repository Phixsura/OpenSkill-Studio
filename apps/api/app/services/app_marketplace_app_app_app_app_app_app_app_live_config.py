"""Live config reloader — hot-reload configuration without restart."""
from __future__ import annotations
import hashlib
import time

_config: dict = {}
_version: int = 0
_history: list[dict] = []


def load_config(config: dict) -> dict:
    global _config, _version
    old_hash = hashlib.sha256(str(_config).encode()).hexdigest()[:8]
    new_hash = hashlib.sha256(str(config).encode()).hexdigest()[:8]
    changed = old_hash != new_hash
    if changed:
        _version += 1
        _history.append({"version": _version, "hash": new_hash, "timestamp": time.time(),
                          "keys_changed": sorted(set(config) ^ set(_config) | {k for k in config if config.get(k) != _config.get(k)})})
    _config = {**config}
    return {"loaded": True, "version": _version, "changed": changed, "hash": new_hash,
            "key_count": len(config)}


def get_config() -> dict:
    return {"config": {**_config}, "version": _version, "key_count": len(_config)}


def config_history(limit: int = 10) -> list[dict]:
    return list(reversed(_history[-limit:]))


def reset_config() -> None:
    global _config, _version
    _config = {}
    _version = 0
    _history.clear()
