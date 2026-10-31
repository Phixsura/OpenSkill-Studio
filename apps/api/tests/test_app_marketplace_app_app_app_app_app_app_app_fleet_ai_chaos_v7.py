from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_chaos_v7 import fleet_ai_chaos_v7
def test_cv7():
    r = fleet_ai_chaos_v7([{"active": True, "experiments": 500, "blast_pct": 5, "recovery_s": 10}])
    assert r["experiments"] == 500
    assert r["resilient"]
