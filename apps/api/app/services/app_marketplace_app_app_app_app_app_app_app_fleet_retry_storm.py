"""Fleet retry storm — detect cascading retry amplification."""
from __future__ import annotations
def fleet_retry_storm(services: list[dict]) -> dict:
    amplification = [s for s in services if s.get("retry_ratio", 0) > 3]
    max_ratio = max((s.get("retry_ratio", 0) for s in services), default=0)
    return {"total": len(services), "amplifying": len(amplification),
            "max_retry_ratio": max_ratio, "storm": len(amplification) > 2}
