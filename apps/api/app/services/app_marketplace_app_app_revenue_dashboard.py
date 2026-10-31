"""App revenue dashboard — comprehensive revenue analytics."""


def build_revenue_dashboard(*, monthly_data: list[dict]) -> dict:
    if not monthly_data:
        return {"error": "No revenue data"}
    total_revenue = round(sum(m.get("revenue", 0) for m in monthly_data), 2)
    total_fees = round(sum(m.get("fees", 0) for m in monthly_data), 2)
    net = round(total_revenue - total_fees, 2)
    mrr = monthly_data[-1].get("revenue", 0) if monthly_data else 0
    arr = round(mrr * 12, 2)
    growth_rates = []
    for i in range(1, len(monthly_data)):
        prev = monthly_data[i - 1].get("revenue", 0)
        curr = monthly_data[i].get("revenue", 0)
        if prev > 0:
            growth_rates.append(round((curr - prev) / prev * 100, 1))
    avg_growth = round(sum(growth_rates) / max(len(growth_rates), 1), 1) if growth_rates else 0
    return {
        "total_revenue": total_revenue,
        "total_fees": total_fees,
        "net_revenue": net,
        "mrr": mrr,
        "arr": arr,
        "avg_monthly_growth": avg_growth,
        "months": len(monthly_data),
        "monthly_data": monthly_data,
    }
