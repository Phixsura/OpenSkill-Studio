from app.services.app_marketplace_app_app_app_app_app_app_app_billing_invoice import generate_invoice

def test_invoice():
    r = generate_invoice(org_name="Acme Corp", plan="pro", period="October 2026",
                           line_items=[
                               {"description": "Pro Plan", "quantity": 1, "unit_price": 99, "amount": 99},
                               {"description": "API Overage (50K calls)", "quantity": 50, "unit_price": 0.001, "amount": 50},
                           ], tax_rate=10)
    assert r["invoice_id"].startswith("INV-")
    assert r["subtotal"] == 149
    assert r["tax"] == 14.9
    assert r["total"] == 163.9
    assert r["item_count"] == 2
    assert r["total_display"] == "$163.90"
