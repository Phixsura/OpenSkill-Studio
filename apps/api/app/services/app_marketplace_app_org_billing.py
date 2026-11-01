"""Org billing — organization-level billing and invoicing."""

from datetime import datetime


def generate_invoice(*, org_id: str, org_name: str, period: str,
                       line_items: list[dict]) -> dict:
    subtotal = round(sum(item.get("amount", 0) for item in line_items), 2)
    tax_rate = 0.0  # simplified
    tax = round(subtotal * tax_rate, 2)
    total = round(subtotal + tax, 2)
    return {
        "invoice_id": f"INV-{org_id[:4].upper()}-{period.replace('-', '')}",
        "org_id": org_id,
        "org_name": org_name,
        "period": period,
        "line_items": line_items,
        "subtotal": subtotal,
        "tax": tax,
        "total": total,
        "currency": "USD",
        "status": "paid" if total == 0 else "due",
        "generated_at": datetime.utcnow().isoformat(),
    }


def get_billing_summary(*, invoices: list[dict]) -> dict:
    total_paid = round(sum(i.get("total", 0) for i in invoices if i.get("status") == "paid"), 2)
    total_due = round(sum(i.get("total", 0) for i in invoices if i.get("status") == "due"), 2)
    return {
        "total_invoices": len(invoices),
        "total_paid": total_paid,
        "total_due": total_due,
        "has_outstanding": total_due > 0,
    }
