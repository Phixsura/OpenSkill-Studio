from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_calico import fleet_calico_status
def test_calico():
    r = fleet_calico_status([{"felix_ready": True, "network_policies": 50}, {"felix_ready": True, "network_policies": 30}])
    assert r["total_policies"] == 80
    assert r["all_healthy"]
