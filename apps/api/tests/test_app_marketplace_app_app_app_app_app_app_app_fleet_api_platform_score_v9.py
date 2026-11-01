from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_platform_score_v9 import fleet_api_platform_score_v9
def test_aps2_v9():
    r = fleet_api_platform_score_v9()
    assert r["score"] == 99
    assert r["grade"] == "A+"
    assert r["dora"] == "ELITE"
    assert "NEVER STOPS" in r["status"]
