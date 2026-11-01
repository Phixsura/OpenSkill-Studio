from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_platform_sre_v8 import fleet_ai_sre_v8
def test_sv8():
    r = fleet_ai_sre_v8([{"active": True, "toil_pct": 10, "budget_pct": 80, "slos": 300}])
    assert r["slos"] == 300
    assert r["elite"]
