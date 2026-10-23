"""Developer analytics v2 — cohort analysis, LTV prediction, engagement metrics."""

from collections import defaultdict
import math


def compute_engagement_score(*, daily_active: int, monthly_active: int, api_calls: int,
                                features_used: int, total_features: int) -> dict:
    dau_mau = round(daily_active / max(monthly_active, 1) * 100, 1)
    feature_adoption = round(features_used / max(total_features, 1) * 100, 1)
    api_intensity = min(100, round(math.log10(max(api_calls, 1)) * 20))
    score = round(dau_mau * 0.4 + feature_adoption * 0.3 + api_intensity * 0.3, 1)
    return {"score": score, "dau_mau_ratio": dau_mau, "feature_adoption": feature_adoption,
            "api_intensity": api_intensity, "tier": "power" if score > 70 else "regular" if score > 30 else "casual"}


def predict_ltv(*, avg_monthly_revenue: float, churn_rate: float) -> dict:
    if churn_rate <= 0:
        return {"ltv": float("inf"), "months": 999, "confidence": "low"}
    months = round(1 / (churn_rate / 100))
    ltv = round(avg_monthly_revenue * months, 2)
    return {"ltv": ltv, "months": months, "confidence": "high" if months < 100 else "medium"}


def build_cohort_table(*, installs: list[dict], retention_data: dict[str, list[float]]) -> list[dict]:
    rows = []
    for cohort, retentions in sorted(retention_data.items()):
        rows.append({"cohort": cohort, "size": len([i for i in installs if i.get("cohort") == cohort]),
                      "retention_pcts": retentions})
    return rows
