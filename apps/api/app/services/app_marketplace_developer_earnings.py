"""Developer earnings — revenue tracking and payout management."""

from collections import defaultdict


def compute_earnings(*, transactions: list[dict]) -> dict:
    total = sum(t.get("amount_cents", 0) for t in transactions)
    by_app = defaultdict(int)
    by_month = defaultdict(int)
    for t in transactions:
        by_app[t.get("app_id", "unknown")] += t.get("amount_cents", 0)
        month = t.get("date", "")[:7]
        if month:
            by_month[month] += t.get("amount_cents", 0)
    platform_fee_pct = 15
    platform_fee = int(total * platform_fee_pct / 100)
    net = total - platform_fee
    return {"gross_cents": total, "platform_fee_cents": platform_fee,
            "net_cents": net, "fee_pct": platform_fee_pct,
            "by_app": dict(sorted(by_app.items(), key=lambda x: -x[1])),
            "by_month": dict(sorted(by_month.items()))}


def get_payout_schedule(*, balance_cents: int, min_payout: int = 5000) -> dict:
    eligible = balance_cents >= min_payout
    return {"balance_cents": balance_cents, "min_payout_cents": min_payout,
            "eligible": eligible, "remaining": max(0, min_payout - balance_cents),
            "balance": f"${balance_cents / 100:,.2f}"}


def compute_lifetime_earnings(*, yearly_earnings: dict[str, int]) -> dict:
    total = sum(yearly_earnings.values())
    return {"lifetime_cents": total, "lifetime": f"${total / 100:,.2f}",
            "years": len(yearly_earnings), "yearly": yearly_earnings}
