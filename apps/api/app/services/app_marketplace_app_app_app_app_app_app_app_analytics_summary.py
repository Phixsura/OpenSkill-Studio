"""Platform analytics summary — aggregate KPIs across the entire platform."""
from __future__ import annotations


def compute_analytics(*, dau: int, mau: int, api_calls_today: int,
                        revenue_mtd: float, new_apps_mtd: int,
                        avg_session_min: float, nps_score: int,
                        churn_rate_pct: float, support_tickets_open: int) -> dict:
    dau_mau_ratio = round(dau / max(mau, 1) * 100, 1)
    engagement = "high" if dau_mau_ratio >= 20 else "medium" if dau_mau_ratio >= 10 else "low"
    health_indicators = []
    if nps_score >= 50:
        health_indicators.append({"metric": "NPS", "status": "excellent", "value": nps_score})
    elif nps_score >= 0:
        health_indicators.append({"metric": "NPS", "status": "good", "value": nps_score})
    else:
        health_indicators.append({"metric": "NPS", "status": "poor", "value": nps_score})
    if churn_rate_pct <= 2:
        health_indicators.append({"metric": "Churn", "status": "excellent", "value": churn_rate_pct})
    elif churn_rate_pct <= 5:
        health_indicators.append({"metric": "Churn", "status": "good", "value": churn_rate_pct})
    else:
        health_indicators.append({"metric": "Churn", "status": "poor", "value": churn_rate_pct})
    return {
        "dau": dau, "dau_display": f"{dau:,}",
        "mau": mau, "mau_display": f"{mau:,}",
        "dau_mau_ratio": dau_mau_ratio, "engagement": engagement,
        "api_calls_today": api_calls_today, "api_display": f"{api_calls_today:,}",
        "revenue_mtd": revenue_mtd, "revenue_display": f"${revenue_mtd:,.0f}",
        "new_apps_mtd": new_apps_mtd, "avg_session_min": avg_session_min,
        "nps_score": nps_score, "churn_rate_pct": churn_rate_pct,
        "support_tickets_open": support_tickets_open,
        "health_indicators": health_indicators,
    }
