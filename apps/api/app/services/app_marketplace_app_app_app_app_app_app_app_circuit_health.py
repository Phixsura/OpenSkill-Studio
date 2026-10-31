"""Circuit health monitor — monitor circuit breaker states across the fleet."""
from __future__ import annotations


def fleet_circuit_health(circuits: list[dict]) -> dict:
    by_state = {"closed": 0, "open": 0, "half-open": 0}
    critical_open = []
    for c in circuits:
        state = c.get("state", "closed")
        by_state[state] = by_state.get(state, 0) + 1
        if state == "open" and c.get("critical", False):
            critical_open.append(c["service"])
    overall = "healthy" if by_state["open"] == 0 else (
        "critical" if critical_open else "degraded")
    return {"overall": overall, "by_state": by_state,
            "total": len(circuits), "critical_open": critical_open,
            "open_pct": round(by_state["open"] / max(len(circuits), 1) * 100, 1)}


def recovery_estimate(circuit: dict) -> dict:
    if circuit["state"] != "open":
        return {"service": circuit["service"], "needs_recovery": False}
    recovery_sec = circuit.get("recovery_seconds", 30)
    elapsed = circuit.get("elapsed_seconds", 0)
    remaining = max(0, recovery_sec - elapsed)
    return {"service": circuit["service"], "needs_recovery": True,
            "remaining_seconds": remaining, "will_half_open": remaining == 0}
