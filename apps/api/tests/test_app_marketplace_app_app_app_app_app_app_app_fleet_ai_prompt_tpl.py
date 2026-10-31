from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_prompt_tpl import fleet_ai_prompt_template
def test_pt():
    r = fleet_ai_prompt_template([{"active": True, "templates": 500, "uses_24h": 2000000, "tokens_saved": 100000000}])
    assert r["templates"] == 500
    assert r["reusable"]
