from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_tensorrt import fleet_tensorrt_status
def test_trt():
    r = fleet_tensorrt_status([{"active": True, "throughput_inf_per_sec": 200000, "p99_ms": 3}])
    assert r["throughput"] == 200000
    assert r["optimized"]
