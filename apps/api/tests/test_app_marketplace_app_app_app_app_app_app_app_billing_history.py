from app.services.app_marketplace_app_app_app_app_app_app_app_billing_history import build_billing_history

def test_history():
    invoices = [
        {"id": "inv_1", "amount": 29, "status": "paid", "date": "2026-09-01", "plan": "Pro"},
        {"id": "inv_2", "amount": 29, "status": "paid", "date": "2026-10-01", "plan": "Pro"},
        {"id": "inv_3", "amount": 34.50, "status": "pending", "date": "2026-11-01", "plan": "Pro"},
    ]
    r = build_billing_history(invoices=invoices, total_spent=92.50)
    assert r["total"] == 3
    assert r["paid"] == 2
    assert r["total_spent_display"] == "$92.50"
    assert r["invoices"][0]["date"] == "2026-11-01"  # newest first
