"""A/B test evaluator — evaluate experiment variants and significance."""
from __future__ import annotations
import math


def evaluate_experiment(control: dict, variant: dict) -> dict:
    c_rate = control["conversions"] / max(control["visitors"], 1)
    v_rate = variant["conversions"] / max(variant["visitors"], 1)
    lift = round((v_rate - c_rate) / max(c_rate, 0.0001) * 100, 2)
    # Simplified z-test
    n1, n2 = control["visitors"], variant["visitors"]
    p1, p2 = c_rate, v_rate
    p_pool = (control["conversions"] + variant["conversions"]) / max(n1 + n2, 1)
    se = math.sqrt(max(p_pool * (1 - p_pool) * (1/max(n1,1) + 1/max(n2,1)), 0.0001))
    z = abs(p2 - p1) / se
    significant = z > 1.96
    winner = "variant" if v_rate > c_rate and significant else ("control" if c_rate > v_rate and significant else "inconclusive")
    return {"control_rate": round(c_rate * 100, 2), "variant_rate": round(v_rate * 100, 2),
            "lift_pct": lift, "z_score": round(z, 3), "significant": significant,
            "winner": winner, "confidence": "95%" if significant else "below_95%"}
