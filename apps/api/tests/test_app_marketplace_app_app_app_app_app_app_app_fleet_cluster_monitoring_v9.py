from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cluster_monitoring_v9 import fleet_cluster_monitoring_v9
def test_cmon_v9():
    r = fleet_cluster_monitoring_v9([{"monitoring_enabled": True, "active_alerts": 0, "dashboards": 20}])
    assert r["monitored"] == 1
    assert r["healthy"]
