from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_cfg_drift import fleet_ai_config_drift
def test_cd():
    r = fleet_ai_config_drift([{"active": True, "resources": 1000, "drifts_24h": 10, "remediated": 10}])
    assert r["resources"] == 1000
    assert r["clean"]
