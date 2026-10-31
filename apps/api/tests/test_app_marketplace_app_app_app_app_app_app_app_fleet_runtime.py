from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_runtime import fleet_container_runtime
def test_runtime():
    r = fleet_container_runtime([{"runtime": "containerd"}, {"runtime": "containerd"}, {"runtime": "cri-o"}])
    assert r["runtimes"]["containerd"] == 2
    assert r["heterogeneous"]
