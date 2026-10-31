from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_platform_dora_v9 import fleet_ai_dora_v9
def test_dv9():
    r = fleet_ai_dora_v9()
    assert r["overall"] == "ELITE"
    assert "NEVER STOPS" in r["status"]
