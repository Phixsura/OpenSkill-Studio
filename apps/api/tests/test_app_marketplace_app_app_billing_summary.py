from app.services.app_marketplace_app_app_billing_summary import build_billing_summary

def test_summary():
    plan = {"name": "Pro", "price": 29, "interval": "monthly", "status": "active"}
    usage = [
        {"name": "API Calls", "quantity": 50000, "unit_price": 0.001, "cost": 50},
        {"name": "Storage", "quantity": 10, "unit_price": 0.5, "cost": 5},
    ]
    invoices = [
        {"id": "inv_1", "amount": 29, "status": "paid", "date": "2026-01-01"},
        {"id": "inv_2", "amount": 84, "status": "paid", "date": "2026-02-01"},
    ]
    r = build_billing_summary(plan=plan, usage=usage, invoices=invoices)
    assert r["plan"]["name"] == "Pro"
    assert r["current_usage"] == 55.0
    assert r["total_charges"] == 113
    assert len(r["invoices"]) == 2
