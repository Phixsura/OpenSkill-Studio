from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_db_proxy_v9 import fleet_db_proxy_v9
def test_dbp_v9():
    r = fleet_db_proxy_v9([{"active": 50, "idle": 30, "max": 200}])
    assert r["utilization_pct"] == 25.0
    assert r["healthy"]
