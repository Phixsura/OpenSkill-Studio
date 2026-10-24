from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_deno import fleet_deno_status
def test_deno():
    r = fleet_deno_status([{"deployed": True, "requests_24h": 2000000, "avg_isolate_ms": 10}])
    assert r["requests_24h"] == 2000000
    assert r["fast"]
