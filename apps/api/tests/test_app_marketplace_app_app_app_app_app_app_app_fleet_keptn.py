from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_keptn import fleet_keptn_status
def test_keptn():
    r = fleet_keptn_status([{"phase": "deployed"}, {"phase": "evaluating"}, {"phase": "deployed"}])
    assert r["deployed"] == 2
    assert r["healthy"]
