"""Platform event router — route events to handlers by topic pattern."""
from __future__ import annotations
import re


_routes: list[dict] = []


def add_route(pattern: str, handler: str, priority: int = 100) -> dict:
    compiled = re.compile(pattern.replace("*", "[^.]+").replace("#", ".*"))
    route = {"pattern": pattern, "handler": handler, "priority": priority,
             "_regex": compiled, "hit_count": 0}
    _routes.append(route)
    _routes.sort(key=lambda r: r["priority"])
    return {"added": True, "pattern": pattern, "handler": handler}


def route_event(topic: str) -> dict:
    matched = []
    for r in _routes:
        if r["_regex"].fullmatch(topic):
            r["hit_count"] += 1
            matched.append({"handler": r["handler"], "pattern": r["pattern"]})
    return {"topic": topic, "matched": matched, "handler_count": len(matched),
            "routed": len(matched) > 0}


def router_stats() -> dict:
    return {"total_routes": len(_routes),
            "routes": [{"pattern": r["pattern"], "handler": r["handler"],
                        "hits": r["hit_count"]} for r in _routes]}


def clear_routes() -> None:
    _routes.clear()
