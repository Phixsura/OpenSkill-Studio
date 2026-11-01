"""Revenue forecast — project future revenue based on trends."""

from datetime import datetime, timedelta


def forecast_revenue(*, monthly_revenues: list[float], months_ahead: int = 3) -> dict:
    if len(monthly_revenues) < 2:
        return {"error": "Need at least 2 months of data"}
    avg_growth = sum(
        (monthly_revenues[i] - monthly_revenues[i - 1]) / max(monthly_revenues[i - 1], 1)
        for i in range(1, len(monthly_revenues))
    ) / (len(monthly_revenues) - 1)
    last = monthly_revenues[-1]
    projections = []
    for m in range(1, months_ahead + 1):
        projected = round(last * (1 + avg_growth) ** m, 2)
        projections.append({
            "month": m,
            "projected_revenue": max(projected, 0),
            "confidence": round(max(0.95 - m * 0.1, 0.5), 2),
        })
    total_historical = round(sum(monthly_revenues), 2)
    total_projected = round(sum(p["projected_revenue"] for p in projections), 2)
    return {
        "avg_growth_rate": round(avg_growth * 100, 2),
        "last_month": last,
        "projections": projections,
        "total_historical": total_historical,
        "total_projected": total_projected,
    }
