"""Billing invoice — generate and format marketplace billing invoices."""
from __future__ import annotations
import html
import secrets


def generate_invoice(*, org_name: str, plan: str, period: str,
                       line_items: list[dict], tax_rate: float = 0) -> dict:
    invoice_id = f"INV-{secrets.token_hex(4).upper()}"
    subtotal = sum(item.get("amount", 0) for item in line_items)
    tax = round(subtotal * tax_rate / 100, 2)
    total = round(subtotal + tax, 2)
    items = [{"description": html.escape(i.get("description", "")),
              "quantity": i.get("quantity", 1),
              "unit_price": i.get("unit_price", 0),
              "amount": i.get("amount", 0),
              "amount_display": f"${i.get('amount', 0):,.2f}"}
             for i in line_items]
    return {
        "invoice_id": invoice_id, "org_name": html.escape(org_name),
        "plan": plan, "period": period,
        "items": items, "item_count": len(items),
        "subtotal": subtotal, "subtotal_display": f"${subtotal:,.2f}",
        "tax": tax, "tax_display": f"${tax:,.2f}",
        "tax_rate": tax_rate,
        "total": total, "total_display": f"${total:,.2f}",
        "status": "paid",
    }
