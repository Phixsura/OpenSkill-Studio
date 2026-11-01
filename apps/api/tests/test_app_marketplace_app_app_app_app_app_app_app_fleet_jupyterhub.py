from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_jupyterhub import fleet_jupyterhub_status
def test_jh():
    r = fleet_jupyterhub_status([{"running": True, "active_users": 500, "servers": 500}])
    assert r["active_users"] == 500
    assert r["all_running"]
