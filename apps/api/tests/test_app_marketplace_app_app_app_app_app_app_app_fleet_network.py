from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_network import fleet_network_throughput
def test_throughput():
    r = fleet_network_throughput([{"rx_mbps": 100, "tx_mbps": 50}, {"rx_mbps": 200, "tx_mbps": 150}])
    assert r["rx_mbps"] == 300
    assert r["tx_mbps"] == 200
    assert r["total_mbps"] == 500
