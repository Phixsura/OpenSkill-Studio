"""API gateway middleware — compose request processing pipelines."""
from __future__ import annotations
import time
import html


def create_middleware_chain(middlewares: list[dict]) -> dict:
    chain = []
    for i, m in enumerate(middlewares):
        chain.append({"order": i, "name": m["name"], "type": m.get("type", "transform"),
                       "enabled": m.get("enabled", True),
                       "config": m.get("config", {})})
    enabled = sum(1 for c in chain if c["enabled"])
    return {"chain": chain, "total": len(chain), "enabled": enabled}


def process_request(chain: dict, request: dict) -> dict:
    applied = []
    latency_ms = 0
    for mw in chain["chain"]:
        if not mw["enabled"]:
            continue
        start = time.time()
        # Simulate middleware processing
        if mw["type"] == "auth":
            if not request.get("token"):
                return {"processed": False, "blocked_by": mw["name"], "reason": "no_token"}
        elif mw["type"] == "rate_limit":
            pass  # simulated
        applied.append(mw["name"])
        latency_ms += 0.5  # simulated
    return {"processed": True, "applied": applied, "middleware_count": len(applied),
            "overhead_ms": round(latency_ms, 1)}
