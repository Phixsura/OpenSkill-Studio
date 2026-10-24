from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_waypoint import fleet_waypoint_status
def test_wp():
    r = fleet_waypoint_status([{"status": "SUCCESS", "released": True}, {"status": "SUCCESS", "released": False}])
    assert r["successful"] == 2
    assert r["unreleased"] == 1
