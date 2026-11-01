from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_platform_sustainability_v8 import fleet_ai_sustainability_v8
def test_sv8():
    r = fleet_ai_sustainability_v8([{"active": True, "carbon_kg": 5000, "renewable_pct": 98, "pue": 1.05}])
    assert r["green"]
