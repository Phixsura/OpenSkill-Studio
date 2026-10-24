from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_change_appr import fleet_change_approval
def test_appr():
    r = fleet_change_approval([{"approved": True}, {"approved": False, "type": "emergency"}, {"approved": True}])
    assert r["approved"] == 2
    assert r["emergency"] == 1
    assert not r["compliant"]
