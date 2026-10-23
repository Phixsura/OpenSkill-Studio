from app.services.app_marketplace_app_org_billing import generate_invoice, get_billing_summary

def test_invoice():
    items = [{"description": "Pro Plan", "amount": 99}, {"description": "Extra storage", "amount": 10}]
    r = generate_invoice(org_id="org1", org_name="Acme", period="2026-10", line_items=items)
    assert r["invoice_id"].startswith("INV-")
    assert r["total"] == 109
    assert r["status"] == "due"

def test_free():
    r = generate_invoice(org_id="org1", org_name="X", period="2026-10", line_items=[])
    assert r["total"] == 0
    assert r["status"] == "paid"

def test_summary():
    invoices = [{"total": 99, "status": "paid"}, {"total": 109, "status": "due"}]
    r = get_billing_summary(invoices=invoices)
    assert r["total_paid"] == 99
    assert r["total_due"] == 109
    assert r["has_outstanding"]
