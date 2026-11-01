"""Billing history — complete invoice and payment history page."""

import html
from datetime import datetime, timezone


def build_billing_history(*, invoices: list[dict], total_spent: float = 0) -> dict:
    items = []
    for inv in sorted(invoices, key=lambda i: i.get("date", ""), reverse=True):
        items.append({
            "id": inv.get("id", ""),
            "amount": inv.get("amount", 0),
            "amount_display": f"${inv.get('amount', 0):.2f}",
            "status": inv.get("status", "paid"),
            "date": inv.get("date", ""),
            "plan": html.escape(inv.get("plan", "Free")),
            "payment_method": inv.get("payment_method", ""),
        })
    paid = sum(1 for i in items if i["status"] == "paid")
    return {"invoices": items[:24], "total": len(items), "paid": paid,
            "total_spent": round(total_spent, 2),
            "total_spent_display": f"${total_spent:,.2f}"}
