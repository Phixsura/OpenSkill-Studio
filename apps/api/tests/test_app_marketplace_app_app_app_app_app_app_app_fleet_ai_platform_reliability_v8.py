from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_platform_reliability_v8 import fleet_ai_reliability_v8
def test_rv8():
    r = fleet_ai_reliability_v8([{"active": True, "uptime_pct": 99.9999, "mttr_min": 3, "budget_pct": 80}])
    assert r["five_nines"]
