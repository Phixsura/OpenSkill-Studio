from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_argo_workflow_v9 import fleet_argo_workflow_v9
def test_argo_v9():
    r = fleet_argo_workflow_v9([{"phase": "Succeeded"}, {"phase": "Running"}])
    assert r["succeeded"] == 1
    assert r["healthy"]
