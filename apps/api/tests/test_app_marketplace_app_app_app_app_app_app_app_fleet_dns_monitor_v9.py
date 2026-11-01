from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_dns_monitor_v9 import fleet_dns_monitor_v9
def test_dm_v9():
    r = fleet_dns_monitor_v9([{"resolving": True, "ttl_sec": 300, "failures_today": 0}])
    assert r["resolving"] == 1
    assert r["healthy"]
