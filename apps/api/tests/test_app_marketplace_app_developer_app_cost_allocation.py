from app.services.app_marketplace_app_developer_app_cost_allocation import allocate_costs, compute_cost_trend, build_cost_report

def test_allocate():
    apps = [{"id": "a1", "usage_units": 70}, {"id": "a2", "usage_units": 30}]
    r = allocate_costs(apps=apps, total_cost_cents=10000)
    assert r[0]["app_id"] == "a1"
    assert r[0]["cost_cents"] == 7000

def test_equal():
    apps = [{"id": "a1", "usage_units": 0}, {"id": "a2", "usage_units": 0}]
    r = allocate_costs(apps=apps, total_cost_cents=10000)
    assert r[0]["cost_cents"] == 5000

def test_trend_up():
    costs = [{"total_cents": 5000}, {"total_cents": 8000}]
    r = compute_cost_trend(monthly_costs=costs)
    assert r["trend"] == "up"

def test_trend_stable():
    costs = [{"total_cents": 5000}, {"total_cents": 5100}]
    r = compute_cost_trend(monthly_costs=costs)
    assert r["trend"] == "stable"

def test_report():
    allocs = [{"app_id": "a1", "cost_cents": 7000}, {"app_id": "a2", "cost_cents": 3000}]
    r = build_cost_report(allocations=allocs, period="2026-10", total_cents=10000)
    assert r["top_spender"] == "a1"
    assert "$100.00" in r["total"]
