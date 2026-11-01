from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_plat_svless_v2 import fleet_ai_serverless_v2
def test_sv2():
    r = fleet_ai_serverless_v2([{"active": True, "functions": 1000, "invocations": 100000000, "cold_ms": 100}])
    assert r["functions"] == 1000
    assert r["warm"]
