"""SLA tracker — track SLA compliance per service."""
from __future__ import annotations

def check_sla(service: str, uptime_pct: float, target: float, p99_ms: float, max_p99: float) -> dict:
    uptime_met = uptime_pct >= target
    latency_met = p99_ms <= max_p99
    compliant = uptime_met and latency_met
    return {"service": service, "compliant": compliant, "uptime_pct": uptime_pct,
            "uptime_target": target, "uptime_met": uptime_met,
            "p99_ms": p99_ms, "max_p99_ms": max_p99, "latency_met": latency_met}

def fleet_sla(services: list[dict]) -> dict:
    compliant = sum(1 for s in services if s["compliant"])
    return {"total": len(services), "compliant": compliant,
            "non_compliant": len(services) - compliant,
            "compliance_pct": round(compliant / max(len(services), 1) * 100, 1)}
