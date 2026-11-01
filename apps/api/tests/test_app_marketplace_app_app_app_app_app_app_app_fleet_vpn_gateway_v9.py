from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_vpn_gateway_v9 import fleet_vpn_gateway_v9
def test_vpn_v9():
    r = fleet_vpn_gateway_v9([{"status": "up", "bandwidth_mbps": 1000, "peer": "office"}])
    assert r["up"] == 1
    assert r["healthy"]
