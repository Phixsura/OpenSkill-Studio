from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ray_serve import fleet_ray_serve
def test_rs():
    r = fleet_ray_serve([{"status": "RUNNING", "replicas": 10, "qps": 5000}])
    assert r["replicas"] == 10
    assert r["all_running"]
