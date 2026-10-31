from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_model_diff import fleet_ai_model_diff
def test_md():
    r = fleet_ai_model_diff([{"active": True, "diffs_24h": 500, "regressions": 10, "improvements": 50}])
    assert r["diffs_24h"] == 500
    assert r["insightful"]
