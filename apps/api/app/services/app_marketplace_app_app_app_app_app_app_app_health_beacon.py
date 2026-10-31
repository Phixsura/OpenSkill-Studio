"""Platform health beacon — emit periodic health signals."""
from __future__ import annotations
import time
import hashlib


def emit_beacon(service: str, status: str = "healthy", metrics: dict | None = None) -> dict:
    beacon_id = hashlib.sha256(f"{service}:{time.time()}".encode()).hexdigest()[:10]
    return {"beacon_id": beacon_id, "service": service, "status": status,
            "metrics": metrics or {}, "emitted_at": time.time()}


def aggregate_beacons(beacons: list[dict]) -> dict:
    by_status: dict[str, int] = {}
    services = set()
    for b in beacons:
        by_status[b["status"]] = by_status.get(b["status"], 0) + 1
        services.add(b["service"])
    healthy = by_status.get("healthy", 0)
    total = len(beacons)
    return {"total_beacons": total, "unique_services": len(services),
            "by_status": by_status, "healthy_pct": round(healthy / max(total, 1) * 100),
            "all_healthy": healthy == total}


def stale_services(beacons: list[dict], max_age_sec: int = 60, now: float | None = None) -> list[str]:
    now = now or time.time()
    latest: dict[str, float] = {}
    for b in beacons:
        svc = b["service"]
        if svc not in latest or b["emitted_at"] > latest[svc]:
            latest[svc] = b["emitted_at"]
    return sorted(svc for svc, ts in latest.items() if now - ts > max_age_sec)
