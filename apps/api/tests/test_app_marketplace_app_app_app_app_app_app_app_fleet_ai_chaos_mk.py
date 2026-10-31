from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_chaos_mk import fleet_ai_chaos_monkey
def test_cm():
    r = fleet_ai_chaos_monkey([{"active": True, "injections_24h": 100, "recovered": 99, "unrecovered": 1}])
    assert r["recovery_rate"] == 99.0
    assert r["resilient"]
