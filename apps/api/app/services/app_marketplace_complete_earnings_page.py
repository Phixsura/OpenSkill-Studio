"""Complete earnings page — revenue dashboard with payouts, projections, and tax info."""

from collections import defaultdict


def build_complete_earnings_page(*, developer: dict, transactions: list[dict],
                                     payouts: list[dict], tax_info: dict | None) -> dict:
    gross = sum(t.get("amount_cents", 0) for t in transactions)
    platform_fee = int(gross * 0.15)
    net = gross - platform_fee
    by_month = defaultdict(int)
    for t in transactions:
        month = t.get("date", "")[:7]
        if month:
            by_month[month] += t.get("amount_cents", 0)
    monthly_data = [{"month": m, "amount_cents": a} for m, a in sorted(by_month.items())]
    pending_payout = sum(p.get("amount_cents", 0) for p in payouts if p.get("status") == "pending")
    return {
        "page_type": "earnings_dashboard",
        "summary": {"gross_cents": gross, "gross": f"${gross / 100:,.2f}",
                      "platform_fee_cents": platform_fee, "net_cents": net,
                      "net": f"${net / 100:,.2f}", "fee_pct": 15},
        "monthly": monthly_data,
        "payouts": {"pending_cents": pending_payout, "total_payouts": len(payouts),
                      "recent": payouts[:5]},
        "tax": {"has_info": tax_info is not None,
                 "country": tax_info.get("country") if tax_info else None,
                 "tax_id": tax_info.get("tax_id") if tax_info else None},
        "tabs": [
            {"key": "overview", "title": "Overview", "icon": "💰"},
            {"key": "transactions", "title": f"Transactions ({len(transactions)})", "icon": "📋"},
            {"key": "payouts", "title": f"Payouts ({len(payouts)})", "icon": "🏦"},
            {"key": "tax", "title": "Tax Info", "icon": "📄"},
        ],
    }
