from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_net_bw import fleet_ai_network_bandwidth
def test_nb():
    r = fleet_ai_network_bandwidth([{"active": True, "ingress_gbps": 100, "egress_gbps": 200, "util_pct": 60}])
    assert r["ingress_gbps"] == 100
    assert r["healthy"]
