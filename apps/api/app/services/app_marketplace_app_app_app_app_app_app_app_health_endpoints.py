"""Health endpoint registry — register and monitor service health endpoints."""
from __future__ import annotations


class HealthEndpointRegistry:
    def __init__(self):
        self._endpoints: dict[str, dict] = {}

    def register(self, service: str, url: str, interval_seconds: int = 30,
                 expected_status: int = 200) -> dict:
        self._endpoints[service] = {"service": service, "url": url,
                                     "interval": interval_seconds,
                                     "expected_status": expected_status,
                                     "last_status": None, "consecutive_failures": 0}
        return self._endpoints[service]

    def record_check(self, service: str, status: int, latency_ms: float) -> dict:
        ep = self._endpoints[service]
        healthy = status == ep["expected_status"]
        if healthy:
            ep["consecutive_failures"] = 0
        else:
            ep["consecutive_failures"] += 1
        ep["last_status"] = status
        ep["last_latency_ms"] = latency_ms
        return {"service": service, "healthy": healthy, "consecutive_failures": ep["consecutive_failures"]}

    def unhealthy_services(self, min_failures: int = 3) -> list[str]:
        return [s for s, ep in self._endpoints.items() if ep["consecutive_failures"] >= min_failures]

    def stats(self) -> dict:
        healthy = sum(1 for ep in self._endpoints.values() if ep.get("consecutive_failures", 0) == 0 and ep["last_status"] is not None)
        checked = sum(1 for ep in self._endpoints.values() if ep["last_status"] is not None)
        return {"total": len(self._endpoints), "healthy": healthy, "checked": checked}
