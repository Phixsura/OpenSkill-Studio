from app.services.app_marketplace_complete_earnings_page import build_complete_earnings_page

def test_earnings():
    p = build_complete_earnings_page(
        developer={"display_name": "DevCo"},
        transactions=[{"amount_cents": 10000, "date": "2026-10-01"}, {"amount_cents": 5000, "date": "2026-10-15"}],
        payouts=[{"amount_cents": 8000, "status": "paid"}, {"amount_cents": 5000, "status": "pending"}],
        tax_info={"country": "US", "tax_id": "XX-1234567"})
    assert p["summary"]["gross_cents"] == 15000
    assert p["summary"]["net_cents"] == 12750
    assert p["payouts"]["pending_cents"] == 5000
    assert p["tax"]["has_info"]
    assert len(p["tabs"]) == 4

def test_no_tax():
    p = build_complete_earnings_page(developer={}, transactions=[], payouts=[], tax_info=None)
    assert not p["tax"]["has_info"]
    assert p["summary"]["gross_cents"] == 0
