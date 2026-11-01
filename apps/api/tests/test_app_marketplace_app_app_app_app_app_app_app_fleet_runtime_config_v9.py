from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_runtime_config_v9 import fleet_runtime_config_v9
def test_rc_v9():
    r = fleet_runtime_config_v9([{"active": True, "has_override": False, "watchers": 50}])
    assert r["active"] == 1
    assert r["healthy"]
