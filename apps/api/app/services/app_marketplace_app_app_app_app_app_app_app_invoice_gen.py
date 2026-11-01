"""Billing invoice generator — create itemized invoices."""
from __future__ import annotations
import hashlib
import time
import html


def generate_invoice(customer: str, items: list[dict], tax_rate: float = 0.0) -> dict:
    inv_id = f"INV-{hashlib.sha256(f'{customer}:{time.time()}'.encode()).hexdigest()[:8].upper()}"
    line_items = []
    subtotal = 0.0
    for item in items:
        qty = item.get("quantity", 1)
        price = item.get("unit_price", 0.0)
        total = round(qty * price, 2)
        subtotal += total
        line_items.append({"description": html.escape(item.get("description", "")),
                           "quantity": qty, "unit_price": price, "total": total})
    tax = round(subtotal * tax_rate, 2)
    grand_total = round(subtotal + tax, 2)
    return {"invoice_id": inv_id, "customer": html.escape(customer),
            "line_items": line_items, "subtotal": subtotal, "tax": tax,
            "tax_rate": tax_rate, "total": grand_total,
            "display_total": f"${grand_total:,.2f}"}


def summarize_invoices(invoices: list[dict]) -> dict:
    total_revenue = sum(i["total"] for i in invoices)
    total_tax = sum(i["tax"] for i in invoices)
    return {"count": len(invoices), "total_revenue": round(total_revenue, 2),
            "total_tax": round(total_tax, 2), "avg_invoice": round(total_revenue / max(len(invoices), 1), 2)}
