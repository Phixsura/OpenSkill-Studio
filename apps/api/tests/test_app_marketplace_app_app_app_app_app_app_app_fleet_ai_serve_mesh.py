from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_serve_mesh import fleet_ai_serving_mesh
def test_sm():
    r = fleet_ai_serving_mesh([{"healthy": True, "rps": 50000, "p99_ms": 45, "gpu_util": 82}])
    assert r["rps"] == 50000
    assert r["optimal"]
