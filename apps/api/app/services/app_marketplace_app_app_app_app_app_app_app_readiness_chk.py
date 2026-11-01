"""Platform readiness checker — verify all systems ready for launch."""
from __future__ import annotations


CHECKLIST = {
    "database": {"category": "infrastructure", "critical": True},
    "cache": {"category": "infrastructure", "critical": True},
    "api": {"category": "services", "critical": True},
    "auth": {"category": "security", "critical": True},
    "monitoring": {"category": "observability", "critical": False},
    "logging": {"category": "observability", "critical": False},
    "backups": {"category": "infrastructure", "critical": True},
    "ssl_certs": {"category": "security", "critical": True},
    "dns": {"category": "infrastructure", "critical": True},
    "ci_cd": {"category": "deployment", "critical": False},
}


def check_readiness(statuses: dict[str, bool]) -> dict:
    results = []
    critical_pass = 0
    critical_total = 0
    for item, info in CHECKLIST.items():
        ready = statuses.get(item, False)
        results.append({"item": item, **info, "ready": ready})
        if info["critical"]:
            critical_total += 1
            if ready:
                critical_pass += 1
    total_ready = sum(1 for r in results if r["ready"])
    launch_ready = critical_pass == critical_total
    return {"checks": results, "total": len(results), "ready": total_ready,
            "not_ready": len(results) - total_ready,
            "critical_pass": critical_pass, "critical_total": critical_total,
            "launch_ready": launch_ready,
            "readiness_pct": round(total_ready / len(results) * 100)}
