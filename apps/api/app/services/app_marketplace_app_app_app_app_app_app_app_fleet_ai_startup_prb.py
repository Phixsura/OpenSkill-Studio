"""Fleet AI Startup Probe — track AI service initialization monitoring."""
from __future__ import annotations
def fleet_ai_startup_probe(probes: list[dict]) -> dict:
    active = [p for p in probes if p.get("active", True)]
    services = sum(p.get("services", 0) for p in probes)
    avg_startup_s = round(sum(p.get("startup_s", 0) for p in probes) / max(len(probes), 1), 1)
    failures_24h = sum(p.get("failures", 0) for p in probes)
    return {"probes": len(probes), "active": len(active), "services": services,
            "startup_s": avg_startup_s, "failures": failures_24h, "healthy": failures_24h == 0}
