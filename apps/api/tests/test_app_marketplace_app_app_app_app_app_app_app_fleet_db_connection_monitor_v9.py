from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_db_connection_monitor_v9 import fleet_db_connection_monitor_v9
def test_dcm_v9():
    r = fleet_db_connection_monitor_v9([{"active": 30, "idle": 20, "max": 100, "waiting": 0}])
    assert r["utilization_pct"] == 30.0
    assert r["healthy"]
