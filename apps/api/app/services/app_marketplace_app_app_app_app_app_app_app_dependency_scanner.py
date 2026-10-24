"""Dependency scanner — detect outdated, vulnerable, and unused dependencies."""
from __future__ import annotations


def scan_dependencies(deps: list[dict]) -> dict:
    results = []
    counts = {"up_to_date": 0, "outdated": 0, "vulnerable": 0, "unused": 0}
    for d in deps:
        name = d.get("name", "")
        current = d.get("current", "0.0.0")
        latest = d.get("latest", current)
        vulns = d.get("vulnerabilities", [])
        used = d.get("used", True)
        status = "vulnerable" if vulns else "unused" if not used else \
                 "outdated" if current != latest else "up_to_date"
        counts[status] += 1
        results.append({
            "name": name, "current": current, "latest": latest,
            "status": status, "vulnerabilities": vulns, "used": used,
            "update_available": current != latest,
        })
    total = len(deps)
    health = round(counts["up_to_date"] / max(total, 1) * 100)
    return {
        "total": total, "counts": counts, "health_score": health,
        "health_display": f"{health}%",
        "action_required": counts["vulnerable"] > 0 or counts["outdated"] > 0,
        "results": sorted(results, key=lambda r: {"vulnerable": 0, "outdated": 1,
                                                    "unused": 2, "up_to_date": 3}[r["status"]]),
    }
