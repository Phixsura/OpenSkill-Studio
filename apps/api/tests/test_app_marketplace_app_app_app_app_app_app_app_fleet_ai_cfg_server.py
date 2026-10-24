from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_cfg_server import fleet_ai_config_server
def test_cs():
    r = fleet_ai_config_server([{"active": True, "configs": 1000, "clients": 500, "updates_24h": 200}])
    assert r["configs"] == 1000
    assert r["serving"]
