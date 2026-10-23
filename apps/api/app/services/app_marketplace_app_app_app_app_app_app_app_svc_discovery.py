"""Service discovery registry — register and discover services."""
from __future__ import annotations
import time

_registry: dict[str, dict] = {}


def register_service(name: str, host: str, port: int, tags: list[str] | None = None,
                      health_url: str = "") -> dict:
    _registry[name] = {"name": name, "host": host, "port": port,
                         "address": f"{host}:{port}", "tags": tags or [],
                         "health_url": health_url, "registered_at": time.time(),
                         "status": "healthy"}
    return _registry[name]


def discover(name: str) -> dict:
    svc = _registry.get(name)
    if not svc:
        return {"found": False, "error": "service_not_found"}
    return {"found": True, **svc}


def discover_by_tag(tag: str) -> list[dict]:
    return [s for s in _registry.values() if tag in s["tags"]]


def deregister(name: str) -> dict:
    if name in _registry:
        del _registry[name]
        return {"deregistered": True}
    return {"deregistered": False, "error": "not_found"}


def registry_overview() -> dict:
    healthy = sum(1 for s in _registry.values() if s["status"] == "healthy")
    all_tags = set()
    for s in _registry.values():
        all_tags.update(s["tags"])
    return {"total": len(_registry), "healthy": healthy,
            "tags": sorted(all_tags), "services": list(_registry.keys())}


def clear_registry() -> None:
    _registry.clear()
