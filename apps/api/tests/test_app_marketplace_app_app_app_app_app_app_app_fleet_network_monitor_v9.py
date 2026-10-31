from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_network_monitor_v9 import fleet_network_monitor_v9
def test_nm_v9():
    r = fleet_network_monitor_v9([{"status": "up", "rx_gbps": 10, "tx_gbps": 8, "errors": 0}])
    assert r["up"] == 1
    assert r["healthy"]
