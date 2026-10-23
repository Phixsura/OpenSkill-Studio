"""A/B test results — statistical analysis of A/B test experiments."""

import math


def analyze_ab_test(*, control: dict, variant: dict) -> dict:
    c_rate = control.get("conversions", 0) / max(control.get("visitors", 1), 1) * 100
    v_rate = variant.get("conversions", 0) / max(variant.get("visitors", 1), 1) * 100
    lift = round((v_rate - c_rate) / max(c_rate, 0.01) * 100, 1)
    # Simplified significance (using sample size heuristic)
    total = control.get("visitors", 0) + variant.get("visitors", 0)
    significant = total >= 1000 and abs(lift) > 5
    winner = "variant" if v_rate > c_rate else "control" if c_rate > v_rate else "tie"
    return {
        "control": {"rate": round(c_rate, 2), "visitors": control.get("visitors", 0),
                     "conversions": control.get("conversions", 0)},
        "variant": {"rate": round(v_rate, 2), "visitors": variant.get("visitors", 0),
                     "conversions": variant.get("conversions", 0)},
        "lift_pct": lift,
        "winner": winner,
        "significant": significant,
        "recommendation": f"Promote {winner}" if significant else "Continue test (need more data)",
    }
