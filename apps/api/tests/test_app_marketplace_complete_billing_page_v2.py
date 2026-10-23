from app.services.app_marketplace_complete_billing_page_v2 import build_complete_billing_page_v2

def test_billing():
    p = build_complete_billing_page_v2(
        developer={"display_name": "DevCo"},
        current_plan={"name": "pro", "price_label": "$99/mo", "renewal_date": "2026-11-01"},
        usage={"api_calls": 50000, "usage_pct": 50, "current_period": "2026-10"},
        invoices=[{"amount_cents": 9900, "status": "paid", "period": "2026-10"}],
        payment_method={"type": "card", "last_four": "4242"},
        cost_breakdown={"api": 5000, "storage": 2000},
        plan_options=[{"name": "enterprise"}])
    assert p["page_type"] == "billing_v2"
    assert p["plan"]["name"] == "pro"
    assert p["payment"]["last_four"] == "4242"
    assert not p["invoices"]["past_due"]
    assert not p["alerts"]["near_limit"]

def test_past_due():
    p = build_complete_billing_page_v2(
        developer={}, current_plan={"name": "starter"},
        usage={"usage_pct": 95, "current_period": "2026-10"},
        invoices=[{"amount_cents": 2900, "status": "past_due", "period": "2026-09"}],
        payment_method=None, cost_breakdown={}, plan_options=[])
    assert p["invoices"]["past_due"]
    assert p["alerts"]["past_due"]
    assert p["alerts"]["near_limit"]
    assert not p["payment"]["has_method"]
