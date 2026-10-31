"""Fleet AI Auto-Complete — track AI-powered text auto-completion."""
from __future__ import annotations
def fleet_ai_autocomplete(engines: list[dict]) -> dict:
    active = [e for e in engines if e.get("active", True)]
    completions_24h = sum(e.get("completions_24h", 0) for e in engines)
    acceptance_rate = round(sum(e.get("acceptance_pct", 0) for e in engines) / max(len(engines), 1), 1)
    avg_latency_ms = round(sum(e.get("latency_ms", 0) for e in engines) / max(len(engines), 1), 1)
    return {"engines": len(engines), "active": len(active), "completions_24h": completions_24h,
            "acceptance_rate": acceptance_rate, "latency_ms": avg_latency_ms, "helpful": acceptance_rate > 30}
