"""Playground environment — isolated sandbox for testing apps."""
from __future__ import annotations
import secrets
import time

_envs: dict[str, dict] = {}


def create_env(owner: str, template: str = "blank", ttl_min: int = 60) -> dict:
    env_id = f"env_{secrets.token_urlsafe(12)}"
    _envs[env_id] = {"id": env_id, "owner": owner, "template": template,
                      "status": "running", "created_at": time.time(),
                      "expires_at": time.time() + ttl_min * 60,
                      "resources": {"cpu": "0.5 vCPU", "memory": "512 MB", "storage": "1 GB"}}
    return _envs[env_id]


def stop_env(env_id: str, requester: str) -> dict:
    env = _envs.get(env_id)
    if not env:
        return {"stopped": False, "error": "not_found"}
    if env["owner"] != requester:
        return {"stopped": False, "error": "not_owner"}
    env["status"] = "stopped"
    return {"stopped": True, "id": env_id}


def list_envs(owner: str | None = None) -> list[dict]:
    now = time.time()
    items = list(_envs.values())
    if owner:
        items = [e for e in items if e["owner"] == owner]
    for e in items:
        if e["status"] == "running" and now > e["expires_at"]:
            e["status"] = "expired"
    return items


def env_stats() -> dict:
    running = sum(1 for e in _envs.values() if e["status"] == "running")
    return {"total": len(_envs), "running": running,
            "stopped": len(_envs) - running}


def clear_envs() -> None:
    _envs.clear()
