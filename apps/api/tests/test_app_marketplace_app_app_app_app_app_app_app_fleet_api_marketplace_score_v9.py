from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_marketplace_score_v9 import fleet_api_marketplace_score_v9
def test_ams2_v9():
    r = fleet_api_marketplace_score_v9()
    assert r["grade"] == "A+"
    assert r["healthy"]
