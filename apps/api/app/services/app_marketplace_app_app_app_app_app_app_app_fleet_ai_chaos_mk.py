"""Fleet AI Chaos Monkey — track random failure injection for resilience."""
from __future__ import annotations
def fleet_ai_chaos_monkey(monkeys: list[dict]) -> dict:
    active = [m for m in monkeys if m.get("active", True)]
    injections_24h = sum(m.get("injections_24h", 0) for m in monkeys)
    recovered = sum(m.get("recovered", 0) for m in monkeys)
    unrecovered = sum(m.get("unrecovered", 0) for m in monkeys)
    recovery_rate = round(recovered / max(recovered + unrecovered, 1) * 100, 1)
    return {"monkeys": len(monkeys), "active": len(active), "injections_24h": injections_24h,
            "recovered": recovered, "unrecovered": unrecovered, "recovery_rate": recovery_rate, "resilient": recovery_rate > 95}
