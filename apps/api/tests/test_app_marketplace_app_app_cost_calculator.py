from app.services.app_marketplace_app_app_cost_calculator import calculate_cost, estimate_monthly

TIERS = [
    {"name": "Free", "from": 0, "to": 1000, "rate": 0},
    {"name": "Standard", "from": 1000, "to": 10000, "rate": 0.01},
    {"name": "Pro", "from": 10000, "to": None, "rate": 0.005},
]

def test_free_tier():
    r = calculate_cost(tiers=TIERS, usage=500)
    assert r["total_cost"] == 0

def test_standard():
    r = calculate_cost(tiers=TIERS, usage=5000)
    assert r["total_cost"] == 40.0  # 1000 free + 4000 * 0.01

def test_all_tiers():
    r = calculate_cost(tiers=TIERS, usage=15000)
    # 1000 free + 9000*0.01 + 5000*0.005 = 0+90+25 = 115
    assert r["total_cost"] == 115.0
    assert r["tier_count"] == 3

def test_monthly():
    r = estimate_monthly(daily_usage=100, tiers=TIERS)
    assert r["monthly_usage"] == 3000
    assert r["total_cost"] == 20.0  # 1000 free + 2000*0.01
