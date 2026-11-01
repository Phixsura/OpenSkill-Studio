"""Fleet AI Traffic Mirror — track AI request mirroring for testing."""
from __future__ import annotations
def fleet_ai_traffic_mirror(mirrors: list[dict]) -> dict:
    active = [m for m in mirrors if m.get("active", True)]
    mirrored_24h = sum(m.get("mirrored_24h", 0) for m in mirrors)
    targets = sum(m.get("targets", 0) for m in mirrors)
    overhead_pct = round(sum(m.get("overhead_pct", 0) for m in mirrors) / max(len(mirrors), 1), 1)
    return {"mirrors": len(mirrors), "active": len(active), "mirrored_24h": mirrored_24h,
            "targets": targets, "overhead_pct": overhead_pct, "low_overhead": overhead_pct < 5}
