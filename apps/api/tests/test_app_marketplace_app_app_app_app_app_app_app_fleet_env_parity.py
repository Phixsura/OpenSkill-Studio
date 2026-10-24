from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_env_parity import fleet_env_parity
def test_parity():
    r = fleet_env_parity([{"config_matches_prod": True}, {"config_matches_prod": False}])
    assert r["drifted"] == 1
    assert not r["parity"]
