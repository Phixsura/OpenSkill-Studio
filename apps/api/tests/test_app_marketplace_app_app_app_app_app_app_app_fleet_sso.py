from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_sso import fleet_sso_status
def test_sso():
    r = fleet_sso_status([{"status": "healthy"}, {"status": "degraded"}, {"status": "down"}])
    assert r["healthy"] == 1
    assert r["degraded"] == 1
    assert r["down"] == 1
    assert not r["all_ok"]
