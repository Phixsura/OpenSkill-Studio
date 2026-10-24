from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_dx_score import fleet_dx_score
def test_dx():
    r = fleet_dx_score({"onboarding": 85, "docs_quality": 90, "sdk_quality": 80, "api_consistency": 95})
    assert r["score"] == 87.5
    assert r["grade"] == "B"
