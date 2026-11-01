from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_plat_net_v4 import fleet_ai_network_v4
def test_nv4():
    r = fleet_ai_network_v4([{"active": True, "bandwidth_gbps": 1000, "latency_ms": 2}])
    assert r["fast"]
