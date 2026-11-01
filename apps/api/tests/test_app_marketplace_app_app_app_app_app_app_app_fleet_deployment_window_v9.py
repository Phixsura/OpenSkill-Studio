from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_deployment_window_v9 import fleet_deployment_window_v9
def test_dw_v9():
    r = fleet_deployment_window_v9([{"status": "open"}, {"status": "closed"}])
    assert r["open"] == 1
    assert r["frozen"] == 0
    assert r["healthy"]
