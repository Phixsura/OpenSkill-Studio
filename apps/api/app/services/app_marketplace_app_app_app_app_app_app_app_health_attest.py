"""Service health attestation — services self-report their health."""
from __future__ import annotations
import time


class HealthAttestation:
    def __init__(self, stale_seconds: int = 60):
        self._attestations: dict[str, dict] = {}
        self._stale_threshold = stale_seconds

    def attest(self, service: str, status: str, details: dict | None = None) -> dict:
        self._attestations[service] = {"service": service, "status": status,
                                        "details": details or {},
                                        "attested_at": time.time()}
        return {"service": service, "attested": True}

    def check(self, service: str, now: float | None = None) -> dict:
        now = now or time.time()
        att = self._attestations.get(service)
        if not att:
            return {"service": service, "status": "unknown", "stale": True}
        age = now - att["attested_at"]
        stale = age > self._stale_threshold
        return {"service": service, "status": att["status"] if not stale else "stale",
                "stale": stale, "age_seconds": round(age)}

    def all_services(self, now: float | None = None) -> dict:
        now = now or time.time()
        results = [self.check(s, now) for s in sorted(self._attestations)]
        healthy = sum(1 for r in results if r["status"] == "healthy")
        return {"services": results, "total": len(results), "healthy": healthy,
                "stale": sum(1 for r in results if r["stale"])}
