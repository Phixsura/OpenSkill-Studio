"""Fleet DNS Security v9 — track DNSSEC and DNS-over-HTTPS."""
from __future__ import annotations
def fleet_dns_security_v9(zones: list[dict]) -> dict:
    dnssec = [z for z in zones if z.get("dnssec_enabled")]
    doh = [z for z in zones if z.get("doh_enabled")]
    queries_blocked = sum(z.get("blocked_queries", 0) for z in zones)
    return {"zones": len(zones), "dnssec_enabled": len(dnssec), "doh_enabled": len(doh),
            "queries_blocked": queries_blocked, "healthy": len(dnssec) == len(zones)}
