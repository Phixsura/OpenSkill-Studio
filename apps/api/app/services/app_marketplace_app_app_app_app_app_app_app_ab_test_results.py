"""A/B test results analyzer — statistical significance and winner detection."""
import math


def analyze_ab_test(*, control_visitors: int, control_conversions: int,
                     variant_visitors: int, variant_conversions: int,
                     confidence_level: float = 0.95) -> dict:
    cr_c = control_conversions / max(control_visitors, 1)
    cr_v = variant_conversions / max(variant_visitors, 1)
    lift = round((cr_v - cr_c) / max(cr_c, 0.0001) * 100, 1)
    n = control_visitors + variant_visitors
    p_pool = (control_conversions + variant_conversions) / max(n, 1)
    se = math.sqrt(max(p_pool * (1 - p_pool) * (1 / max(control_visitors, 1) + 1 / max(variant_visitors, 1)), 0))
    z = abs(cr_v - cr_c) / max(se, 1e-10)
    z_thresh = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}.get(confidence_level, 1.96)
    significant = z >= z_thresh
    winner = "variant" if cr_v > cr_c and significant else "control" if cr_c > cr_v and significant else "none"
    return {
        "control": {"visitors": control_visitors, "conversions": control_conversions,
                     "rate": round(cr_c * 100, 2), "rate_display": f"{cr_c * 100:.2f}%"},
        "variant": {"visitors": variant_visitors, "conversions": variant_conversions,
                     "rate": round(cr_v * 100, 2), "rate_display": f"{cr_v * 100:.2f}%"},
        "lift": lift, "lift_display": f"{'+' if lift > 0 else ''}{lift}%",
        "z_score": round(z, 3), "significant": significant,
        "winner": winner, "confidence": confidence_level,
    }
