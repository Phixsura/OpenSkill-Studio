from app.services.app_marketplace_complete_billing_page import build_complete_billing_page

def test_page():
    p = build_complete_billing_page(
        developer={"display_name": "DevCo"},
        current_plan={"name": "Pro", "price": "$29/mo", "renewal_date": "2026-12-01"},
        usage={"api_calls": 50000}, invoices=[{"id": "inv_1", "amount": 29}],
        cost_estimate={"total_usd": 35})
    assert p["page_type"] == "billing_dashboard"
    assert len(p["sections"]) == 5
    assert "Invoices (1)" in p["sections"][3]["title"]
