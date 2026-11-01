"""Fleet DNS Failover v9 — track DNS-based failover and health checks."""
from __future__ import annotations
def fleet_dns_failover_v9(records: list[dict]) -> dict:
    primary = [r for r in records if r.get("role") == "primary"]
    failover = [r for r in records if r.get("role") == "failover"]
    checks_passing = [r for r in records if r.get("health_check_passing")]
    return {"records": len(records), "primary": len(primary), "failover": len(failover),
            "health_checks_passing": len(checks_passing), "healthy": len(checks_passing) == len(records)}
