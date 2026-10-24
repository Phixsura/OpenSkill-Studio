"""Fleet AI Guardrails — track LLM safety and content filtering."""
from __future__ import annotations
def fleet_ai_guardrails(services: list[dict]) -> dict:
    active = [s for s in services if s.get("active", True)]
    blocked_24h = sum(s.get("blocked_24h", 0) for s in services)
    total_checks = sum(s.get("checks_24h", 0) for s in services)
    block_rate = round(blocked_24h / max(total_checks, 1) * 100, 2)
    return {"services": len(services), "active": len(active), "checks_24h": total_checks,
            "blocked_24h": blocked_24h, "block_rate_pct": block_rate}
