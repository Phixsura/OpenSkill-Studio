"""Fleet Container Probe v9 — track liveness, readiness, startup probes."""
from __future__ import annotations
def fleet_container_probe_v9(containers: list[dict]) -> dict:
    liveness = [c for c in containers if c.get("liveness_probe")]
    readiness = [c for c in containers if c.get("readiness_probe")]
    startup = [c for c in containers if c.get("startup_probe")]
    return {"containers": len(containers), "liveness": len(liveness), "readiness": len(readiness),
            "startup": len(startup), "healthy": len(liveness) == len(containers)}
