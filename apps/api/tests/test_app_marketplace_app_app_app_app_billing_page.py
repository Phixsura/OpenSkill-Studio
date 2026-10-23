from app.services.app_marketplace_app_app_app_app_billing_page import build_billing_page

def test_billing():
    r = build_billing_page(
        org={"name": "Acme"},
        plan={"name": "Pro", "price": 29, "interval": "monthly", "api_limit": 500000, "overage_rate": 0.001},
        usage={"api_calls": 600000, "storage_mb": 512},
        invoices=[{"id": "inv_1", "amount": 29, "status": "paid", "date": "2026-01-01"}],
        payment={"brand": "Visa", "last4": "4242"})
    assert r["plan"]["name"] == "Pro"
    assert r["usage"]["api_pct"] == 120.0
    assert r["billing"]["overage"] == 100.0  # 100K over * 0.001
    assert r["billing"]["total"] == 129.0
    assert r["payment"]["last4"] == "4242"
