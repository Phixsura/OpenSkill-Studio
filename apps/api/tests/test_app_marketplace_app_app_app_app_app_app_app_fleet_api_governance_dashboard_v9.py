from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_governance_dashboard_v9 import fleet_api_governance_dashboard_v9
def test_agov2_v9():
    r = fleet_api_governance_dashboard_v9()
    assert r["score"] == 100
    assert r["governance"]["violations"] == 0
