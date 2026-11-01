from app.services.app_marketplace_app_app_app_app_app_app_app_invoice_gen import generate_invoice, summarize_invoices

def test_invoice():
    r = generate_invoice("Acme Corp", [
        {"description": "API Pro Plan", "quantity": 1, "unit_price": 99.00},
        {"description": "Extra Storage 50GB", "quantity": 2, "unit_price": 10.00},
    ], tax_rate=0.1)
    assert r["subtotal"] == 119.0
    assert r["tax"] == 11.9
    assert r["total"] == 130.9
    assert r["invoice_id"].startswith("INV-")

def test_summary():
    invoices = [
        generate_invoice("A", [{"description": "x", "unit_price": 100}]),
        generate_invoice("B", [{"description": "y", "unit_price": 200}]),
    ]
    s = summarize_invoices(invoices)
    assert s["count"] == 2
    assert s["total_revenue"] == 300.0
    assert s["avg_invoice"] == 150.0
