"""Service health fingerprint — create unique health fingerprints for comparison."""
from __future__ import annotations
import hashlib


def create_fingerprint(service: str, metrics: dict) -> dict:
    data = f"{service}:{metrics.get('uptime_pct', 0)}:{metrics.get('error_rate', 0)}:{metrics.get('p99_ms', 0)}"
    fp = hashlib.sha256(data.encode()).hexdigest()[:16]
    health_level = "green" if metrics.get("uptime_pct", 0) >= 99.9 and metrics.get("error_rate", 100) < 1 else (
        "yellow" if metrics.get("uptime_pct", 0) >= 99 else "red")
    return {"service": service, "fingerprint": fp, "level": health_level,
            "uptime": metrics.get("uptime_pct", 0),
            "error_rate": metrics.get("error_rate", 0),
            "p99_ms": metrics.get("p99_ms", 0)}


def compare_fingerprints(fp1: dict, fp2: dict) -> dict:
    same = fp1["fingerprint"] == fp2["fingerprint"]
    level_changed = fp1["level"] != fp2["level"]
    return {"same_health": same, "level_changed": level_changed,
            "from_level": fp1["level"], "to_level": fp2["level"],
            "service": fp1["service"]}
