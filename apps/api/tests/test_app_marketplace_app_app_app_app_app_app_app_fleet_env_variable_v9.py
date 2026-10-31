from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_env_variable_v9 import fleet_env_variable_v9
def test_ev_v9():
    r = fleet_env_variable_v9([{"encrypted": True, "rotated_recently": True, "env": "prod"}])
    assert r["encrypted"] == 1
    assert r["healthy"]
