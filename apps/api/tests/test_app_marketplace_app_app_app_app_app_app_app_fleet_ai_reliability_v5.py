from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_reliability_v5 import fleet_ai_reliability_v5
def test_rv5():
    r = fleet_ai_reliability_v5([{"active": True, "uptime_pct": 99.9999, "mttr_min": 5, "budget_pct": 80, "slis": 200}])
    assert r["five_nines"]
