"""Fleet AI Token Counter — track real-time token usage metering."""
from __future__ import annotations
def fleet_ai_token_counter(counters: list[dict]) -> dict:
    active = [c for c in counters if c.get("active", True)]
    input_tokens_24h = sum(c.get("input_tokens", 0) for c in counters)
    output_tokens_24h = sum(c.get("output_tokens", 0) for c in counters)
    cost_24h = round(sum(c.get("cost_usd", 0) for c in counters), 2)
    return {"counters": len(counters), "active": len(active), "input_tokens": input_tokens_24h,
            "output_tokens": output_tokens_24h, "cost_usd": cost_24h, "metered": len(active) == len(counters)}
