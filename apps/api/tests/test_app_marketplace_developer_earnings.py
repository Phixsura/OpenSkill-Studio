from app.services.app_marketplace_developer_earnings import compute_earnings, get_payout_schedule, compute_lifetime_earnings

def test_earnings():
    txns = [{"app_id": "a1", "amount_cents": 5000, "date": "2026-10-01"},
            {"app_id": "a1", "amount_cents": 3000, "date": "2026-10-15"},
            {"app_id": "a2", "amount_cents": 2000, "date": "2026-11-01"}]
    e = compute_earnings(transactions=txns)
    assert e["gross_cents"] == 10000
    assert e["net_cents"] == 8500  # 15% fee
    assert e["by_app"]["a1"] == 8000

def test_payout_eligible():
    r = get_payout_schedule(balance_cents=10000)
    assert r["eligible"]

def test_payout_not_eligible():
    r = get_payout_schedule(balance_cents=3000)
    assert not r["eligible"]
    assert r["remaining"] == 2000

def test_lifetime():
    r = compute_lifetime_earnings(yearly_earnings={"2025": 100000, "2026": 200000})
    assert r["lifetime_cents"] == 300000
    assert r["years"] == 2
