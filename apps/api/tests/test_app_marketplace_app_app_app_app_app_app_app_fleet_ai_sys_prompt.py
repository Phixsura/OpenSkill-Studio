from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_sys_prompt import fleet_ai_system_prompt
def test_sp():
    r = fleet_ai_system_prompt([{"active": True, "prompts": 100, "versions": 500, "uses_24h": 10000000}])
    assert r["prompts"] == 100
    assert r["managed"]
