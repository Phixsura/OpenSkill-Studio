from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_blue_green_v9 import fleet_blue_green_v9
def test_bg_v9():
    r = fleet_blue_green_v9([{"env": "blue", "active": True}, {"env": "green", "active": False}])
    assert r["active_env"] == "blue"
    assert r["healthy"]
