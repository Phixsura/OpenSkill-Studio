from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_platform_chaos_v8 import fleet_ai_chaos_v8
def test_cv8():
    r = fleet_ai_chaos_v8([{"active": True, "experiments_24h": 1000, "recovery_s": 10, "blast_pct": 3}])
    assert r["experiments"] == 1000
    assert r["resilient"]
