from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_prompt_reg import fleet_ai_prompt_registry
def test_pr():
    r = fleet_ai_prompt_registry([{"active": True, "templates": 200, "versions": 800}])
    assert r["templates"] == 200
    assert r["versions"] == 800
    assert r["organized"]
