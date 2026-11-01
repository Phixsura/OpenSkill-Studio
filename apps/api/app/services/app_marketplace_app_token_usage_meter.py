"""Token usage meter — track API token consumption for AI-powered features."""


def calculate_token_usage(*, requests: list[dict]) -> dict:
    total_input = sum(r.get("input_tokens", 0) for r in requests)
    total_output = sum(r.get("output_tokens", 0) for r in requests)
    total_tokens = total_input + total_output
    cost_per_1k_input = 0.003
    cost_per_1k_output = 0.015
    cost = round(total_input / 1000 * cost_per_1k_input + total_output / 1000 * cost_per_1k_output, 4)
    return {
        "total_requests": len(requests),
        "total_input_tokens": total_input,
        "total_output_tokens": total_output,
        "total_tokens": total_tokens,
        "estimated_cost": cost,
        "avg_tokens_per_request": round(total_tokens / max(len(requests), 1)),
    }


def check_token_budget(*, used: int, budget: int) -> dict:
    remaining = max(budget - used, 0)
    pct_used = round(used / max(budget, 1) * 100, 1)
    return {
        "used": used,
        "budget": budget,
        "remaining": remaining,
        "pct_used": pct_used,
        "exceeded": used >= budget,
        "warning": pct_used >= 80,
    }
