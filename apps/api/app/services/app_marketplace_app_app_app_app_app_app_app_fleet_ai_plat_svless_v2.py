"""Fleet AI Serverless v2 — track serverless AI function execution at scale."""
from __future__ import annotations
def fleet_ai_serverless_v2(platforms: list[dict]) -> dict:
    active = [p for p in platforms if p.get("active", True)]
    functions = sum(p.get("functions", 0) for p in platforms)
    invocations_24h = sum(p.get("invocations", 0) for p in platforms)
    cold_start_ms = round(sum(p.get("cold_ms", 0) for p in platforms) / max(len(platforms), 1), 1)
    return {"platforms": len(platforms), "active": len(active), "functions": functions,
            "invocations": invocations_24h, "cold_ms": cold_start_ms, "warm": cold_start_ms < 200}
