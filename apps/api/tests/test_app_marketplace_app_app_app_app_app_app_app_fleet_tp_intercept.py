from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_tp_intercept import fleet_tp_intercept
def test_tpi():
    r = fleet_tp_intercept([{"active": True, "type": "personal"}, {"active": True, "type": "global"}, {"active": False}])
    assert r["active"] == 2
    assert r["personal"] == 1
    assert r["in_use"]
