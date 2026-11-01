from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_bluegreen import fleet_bluegreen_status
def test_bg():
    r = fleet_bluegreen_status([{"active": "green", "status": "live"}, {"active": "blue", "status": "switching"}])
    assert r["green_live"] == 1
    assert r["switching"] == 1
    assert not r["stable"]
