from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cfg_validate import fleet_config_validation
def test_cfg():
    r = fleet_config_validation([{"valid": True}, {"valid": False}])
    assert r["invalid"] == 1
    assert not r["safe_to_deploy"]
