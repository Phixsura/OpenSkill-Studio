from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_tekton import fleet_tekton_status
def test_tekton():
    r = fleet_tekton_status([{"status": "Succeeded", "duration_min": 10}, {"status": "Failed"}, {"status": "Running"}])
    assert r["succeeded"] == 1
    assert r["avg_duration_min"] == 10.0
