from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_idp import fleet_idp_metrics
def test_idp():
    r = fleet_idp_metrics({"service_templates": 10, "scaffolds_used_30d": 50, "docs_pages": 200})
    assert r["templates"] == 10
    assert r["adoption_score"] == 40.0  # (50+50+20)/3
