from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_config_server_v9 import fleet_config_server_v9
def test_cfg_v9():
    r = fleet_config_server_v9([{"distributed": True, "version": 5, "watchers": 100}])
    assert r["watchers"] == 100
    assert r["healthy"]
