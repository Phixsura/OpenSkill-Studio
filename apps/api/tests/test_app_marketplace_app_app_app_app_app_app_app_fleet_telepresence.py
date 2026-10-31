from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_telepresence import fleet_telepresence_status
def test_tp():
    r = fleet_telepresence_status([{"connected": True, "intercepts": 3}, {"connected": False}])
    assert r["active"] == 1
    assert r["intercepts"] == 3
    assert r["in_use"]
