"""Platform service registry final — complete registry of all platform services."""
from __future__ import annotations
from collections import defaultdict


def registry_summary(services: list[dict]) -> dict:
    by_module: dict[str, int] = defaultdict(int)
    by_status: dict[str, int] = defaultdict(int)
    for s in services:
        by_module[s.get("module", "other")] += 1
        by_status[s.get("status", "active")] += 1
    return {"total_services": len(services), "by_module": dict(by_module),
            "by_status": dict(by_status), "modules": len(by_module),
            "active": by_status.get("active", 0),
            "all_active": by_status.get("active", 0) == len(services)}


def search_registry(services: list[dict], query: str = "", module: str = "") -> list[dict]:
    results = services
    if query:
        results = [s for s in results if query.lower() in s.get("name", "").lower()]
    if module:
        results = [s for s in results if s.get("module") == module]
    return sorted(results, key=lambda s: s.get("name", ""))
