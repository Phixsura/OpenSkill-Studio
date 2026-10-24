"""Fleet AI Code Generation — track AI-assisted coding."""
from __future__ import annotations
def fleet_ai_codegen(services: list[dict]) -> dict:
    active = [s for s in services if s.get("active", True)]
    completions_24h = sum(s.get("completions_24h", 0) for s in services)
    acceptance_rate = round(sum(s.get("acceptance_pct", 0) for s in services) / max(len(services), 1), 1)
    lines_generated = sum(s.get("lines_generated_24h", 0) for s in services)
    return {"services": len(services), "active": len(active), "completions_24h": completions_24h,
            "acceptance_rate": acceptance_rate, "lines_generated": lines_generated}
