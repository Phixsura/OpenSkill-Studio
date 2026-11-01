from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_data_load_v2 import fleet_ai_data_loader_v2
def test_dlv2():
    r = fleet_ai_data_loader_v2([{"active": True, "throughput_gbps": 100, "prefetch": 16, "workers": 64}])
    assert r["throughput_gbps"] == 100
    assert r["fast"]
