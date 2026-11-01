from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_bun import fleet_bun_status
def test_bun():
    r = fleet_bun_status([{"running": True, "rps": 200000, "startup_ms": 10}])
    assert r["rps"] == 200000
    assert r["instant"]
