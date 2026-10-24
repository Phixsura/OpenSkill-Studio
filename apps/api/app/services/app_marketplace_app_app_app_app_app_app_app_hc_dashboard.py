"""Health check dashboard — unified health view for the entire platform."""
from __future__ import annotations
from collections import defaultdict


def build_dashboard(checks: list[dict]) -> dict:
    by_category: dict[str, list[dict]] = defaultdict(list)
    for c in checks:
        cat = c.get("category", "general")
        status = c.get("status", "unknown")
        by_category[cat].append({"name": c["name"], "status": status,
                                  "latency_ms": c.get("latency_ms", 0),
                                  "message": c.get("message", "")})
    categories = {}
    for cat, items in sorted(by_category.items()):
        healthy = sum(1 for i in items if i["status"] == "healthy")
        categories[cat] = {"items": items, "healthy": healthy,
                           "total": len(items), "all_healthy": healthy == len(items)}
    all_healthy = all(c["all_healthy"] for c in categories.values())
    total = sum(c["total"] for c in categories.values())
    healthy_total = sum(c["healthy"] for c in categories.values())
    return {"categories": categories, "all_healthy": all_healthy,
            "total_checks": total, "healthy_checks": healthy_total,
            "health_pct": round(healthy_total / max(total, 1) * 100, 1)}
