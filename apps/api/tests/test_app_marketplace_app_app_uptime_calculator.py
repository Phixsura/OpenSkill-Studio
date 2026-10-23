from app.services.app_marketplace_app_app_uptime_calculator import calculate_uptime, monthly_budget, annual_budget

def test_uptime():
    r = calculate_uptime(total_minutes=43200, downtime_minutes=43)
    assert r["uptime_pct"] > 99.9
    assert r["nines"] == 3

def test_five_nines():
    r = calculate_uptime(total_minutes=43200, downtime_minutes=0)
    assert r["nines"] == 5

def test_monthly():
    r = monthly_budget(sla_pct=99.9)
    assert r["allowed_downtime_min"] == 43.2

def test_annual():
    r = annual_budget(sla_pct=99.99)
    assert r["allowed_downtime_hours"] < 1
