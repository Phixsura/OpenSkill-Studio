"""Fleet DDoS protection — track DDoS mitigation metrics."""
from __future__ import annotations
def fleet_ddos_status(zones: list[dict]) -> dict:
    under_attack = [z for z in zones if z.get("under_attack", False)]
    mitigated = sum(z.get("mitigated_gbps", 0) for z in zones)
    return {"zones": len(zones), "under_attack": len(under_attack),
            "mitigated_gbps": round(mitigated, 1), "all_clear": len(under_attack) == 0}
