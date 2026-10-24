"""Fleet AI Token Counter — track token usage accounting."""
from __future__ import annotations
def fleet_ai_token_counter(accounts: list[dict]) -> dict:
    total_input = sum(a.get("input_tokens_24h", 0) for a in accounts)
    total_output = sum(a.get("output_tokens_24h", 0) for a in accounts)
    total_cost = sum(a.get("cost_24h", 0) for a in accounts)
    return {"accounts": len(accounts), "input_tokens": total_input, "output_tokens": total_output,
            "total_cost": round(total_cost, 2), "tracked": len(accounts) > 0}
