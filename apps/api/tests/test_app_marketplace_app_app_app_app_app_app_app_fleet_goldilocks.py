from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_goldilocks import fleet_goldilocks
def test_gl():
    r = fleet_goldilocks([{"goldilocks_enabled": True, "recommendations": 50}, {"goldilocks_enabled": False}])
    assert r["enabled"] == 1
    assert r["recommendations"] == 50
    assert not r["adopted"]
