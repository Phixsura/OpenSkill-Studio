from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_argo_wf_ev import fleet_argo_wf_events
def test_ev():
    r = fleet_argo_wf_events([{"triggered_workflow": True}, {"triggered_workflow": False}])
    assert r["triggered_workflows"] == 1
    assert r["trigger_rate"] == 50.0
