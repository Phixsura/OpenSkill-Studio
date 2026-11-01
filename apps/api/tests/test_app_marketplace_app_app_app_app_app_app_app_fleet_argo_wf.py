from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_argo_wf import fleet_argo_workflows
def test_wf():
    r = fleet_argo_workflows([{"phase": "Succeeded", "duration_min": 15}, {"phase": "Failed"}, {"phase": "Running"}])
    assert r["succeeded"] == 1
    assert r["avg_duration_min"] == 15.0
