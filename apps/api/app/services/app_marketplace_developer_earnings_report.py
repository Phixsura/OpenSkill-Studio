"""Developer earnings report — monthly and yearly earnings breakdown."""


def build_earnings_report(*, developer_id: str, monthly_data: list[dict]) -> dict:
    total_gross = sum(m.get("gross", 0) for m in monthly_data)
    total_fees = sum(m.get("fees", 0) for m in monthly_data)
    total_net = round(total_gross - total_fees, 2)
    avg_monthly = round(total_net / max(len(monthly_data), 1), 2)
    best_month = max(monthly_data, key=lambda m: m.get("gross", 0)) if monthly_data else None
    growth = []
    for i in range(1, len(monthly_data)):
        prev = monthly_data[i - 1].get("gross", 0)
        curr = monthly_data[i].get("gross", 0)
        pct = round((curr - prev) / max(prev, 1) * 100, 1)
        growth.append(pct)
    return {
        "developer_id": developer_id,
        "months": len(monthly_data),
        "total_gross": round(total_gross, 2),
        "total_fees": round(total_fees, 2),
        "total_net": total_net,
        "avg_monthly_net": avg_monthly,
        "best_month": best_month.get("month") if best_month else None,
        "avg_growth_pct": round(sum(growth) / max(len(growth), 1), 1) if growth else 0,
    }
