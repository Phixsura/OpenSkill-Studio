"""Fleet DNS health — monitor DNS resolution health."""
from __future__ import annotations
def fleet_dns_health(checks: list[dict]) -> dict:
    healthy = [c for c in checks if c.get("resolved", False)]
    slow = [c for c in checks if c.get("latency_ms", 0) > 100]
    return {"total": len(checks), "healthy": len(healthy), "failed": len(checks) - len(healthy),
            "slow": len(slow), "all_ok": len(healthy) == len(checks) and len(slow) == 0}
