"""Config hot-swap engine — swap configurations without downtime."""
from __future__ import annotations
import hashlib
import time

_active: dict | None = None
_pending: dict | None = None


def stage_config(config: dict) -> dict:
    global _pending
    config_hash = hashlib.sha256(str(sorted(config.items())).encode()).hexdigest()[:10]
    _pending = {"config": config, "hash": config_hash, "staged_at": time.time()}
    return {"staged": True, "hash": config_hash, "key_count": len(config)}


def activate_pending() -> dict:
    global _active, _pending
    if not _pending:
        return {"activated": False, "error": "no_pending_config"}
    old_hash = _active["hash"] if _active else None
    _active = _pending
    _pending = None
    return {"activated": True, "hash": _active["hash"], "previous_hash": old_hash}


def get_active() -> dict:
    if not _active:
        return {"active": False}
    return {"active": True, "config": _active["config"], "hash": _active["hash"]}


def rollback_config(previous: dict) -> dict:
    global _active
    _active = {"config": previous, "hash": hashlib.sha256(str(sorted(previous.items())).encode()).hexdigest()[:10],
                "staged_at": time.time()}
    return {"rolled_back": True, "hash": _active["hash"]}


def reset_hotswap() -> None:
    global _active, _pending
    _active = None
    _pending = None
