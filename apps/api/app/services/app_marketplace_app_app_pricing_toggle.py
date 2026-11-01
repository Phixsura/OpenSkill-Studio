"""Pricing toggle — monthly vs annual billing comparison."""


def calculate_pricing(*, monthly_price: float, annual_discount_pct: float = 20) -> dict:
    annual_monthly = round(monthly_price * (1 - annual_discount_pct / 100), 2)
    annual_total = round(annual_monthly * 12, 2)
    monthly_total = round(monthly_price * 12, 2)
    savings = round(monthly_total - annual_total, 2)
    return {
        "monthly": {"price": monthly_price, "total_yearly": monthly_total, "label": f"${monthly_price}/mo"},
        "annual": {"price": annual_monthly, "total_yearly": annual_total, "label": f"${annual_monthly}/mo",
                    "billed_as": f"${annual_total}/yr"},
        "savings": savings,
        "savings_pct": annual_discount_pct,
        "savings_label": f"Save ${savings}/yr ({annual_discount_pct}% off)",
    }
