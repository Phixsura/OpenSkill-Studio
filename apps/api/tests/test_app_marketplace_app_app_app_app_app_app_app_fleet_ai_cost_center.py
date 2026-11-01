from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_cost_center import fleet_ai_cost_center
def test_cc():
    r = fleet_ai_cost_center([{"active": True, "teams": 30, "total_usd": 2000000, "allocated_pct": 99}])
    assert r["teams"] == 30
    assert r["tracked"]
