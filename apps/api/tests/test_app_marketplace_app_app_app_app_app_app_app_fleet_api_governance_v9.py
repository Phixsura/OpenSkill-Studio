from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_governance_v9 import fleet_api_governance_v9
def test_agov_v9():
    r = fleet_api_governance_v9([{"governance_compliant": True, "design_reviewed": True, "standard": "OpenAPI"}])
    assert r["compliant"] == 1
    assert r["healthy"]
