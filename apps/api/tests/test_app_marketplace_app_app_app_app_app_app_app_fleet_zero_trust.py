from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_zero_trust import fleet_zero_trust
def test_zt():
    r = fleet_zero_trust([{"implemented": True}] * 8 + [{"implemented": False}] * 2)
    assert r["score"] == 80.0
    assert r["mature"]
