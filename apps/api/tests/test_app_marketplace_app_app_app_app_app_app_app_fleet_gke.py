from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_gke import fleet_gke_status
def test_gke():
    r = fleet_gke_status([{"status": "RUNNING", "pods": 500, "autopilot": True}])
    assert r["pods"] == 500
    assert r["autopilot"] == 1
    assert r["all_running"]
