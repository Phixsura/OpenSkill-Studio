from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_net_opt import fleet_ai_network_optimizer
def test_no():
    r = fleet_ai_network_optimizer([{"active": True, "saved_pct": 50, "latency_reduction_pct": 40, "compression_x": 5}])
    assert r["bandwidth_saved"] == 50.0
    assert r["optimized"]
