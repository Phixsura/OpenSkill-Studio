from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_actix import fleet_actix_status
def test_actix():
    r = fleet_actix_status([{"running": True, "rps": 300000, "p99_ms": 2}])
    assert r["rps"] == 300000
    assert r["blazing_fast"]
