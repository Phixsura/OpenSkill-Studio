from app.services.app_marketplace_app_developer_billing_portal import get_billing_overview, generate_invoice_preview, get_plan_comparison

def test_overview():
    o = get_billing_overview(plan={"name": "Pro", "next_billing_date": "2026-11-01"},
                              usage={"api_calls": 50000},
                              invoices=[{"amount_cents": 9900, "status": "paid"}, {"amount_cents": 9900, "status": "pending"}])
    assert o["current_spend_cents"] == 9900
    assert o["invoice_count"] == 2

def test_invoice():
    i = generate_invoice_preview(plan_price=9900, overages={"api_calls": 500, "storage": 200})
    assert i["total_cents"] == 10600
    assert "$106.00" in i["total"]

def test_plans():
    p = get_plan_comparison(current_plan="pro")
    assert len(p) == 4
    pro = next(x for x in p if x["name"] == "Pro")
    assert pro["current"]
