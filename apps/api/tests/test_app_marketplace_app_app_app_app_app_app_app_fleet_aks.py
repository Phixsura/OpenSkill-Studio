from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_aks import fleet_aks_status
def test_aks():
    r = fleet_aks_status([{"power_state": "Running", "nodes": 20, "upgrade_available": True}])
    assert r["nodes"] == 20
    assert r["upgrades_available"] == 1
    assert r["all_running"]
