from app.services.app_marketplace_app_app_org_billing import build_billing_overview

def test_billing():
    r = build_billing_overview(
        plan={"name": "Pro", "price": 29, "interval": "monthly"},
        usage={"api_calls": 350000, "api_limit": 500000, "overage": 5.50, "storage_mb": 512},
        invoices=[{"id": "inv_1", "amount": 29, "status": "paid"}],
        payment_method={"type": "card", "last4": "4242", "brand": "Visa"},
    )
    assert r["plan"]["name"] == "Pro"
    assert r["current_period"]["total"] == 34.50
    assert r["usage_summary"]["api_pct"] == 70.0
    assert r["payment_method"]["last4"] == "4242"
    assert r["has_payment_method"]
