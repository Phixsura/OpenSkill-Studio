from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_green_comp import fleet_ai_green_computing
def test_gc():
    r = fleet_ai_green_computing([{"active": True, "co2_kg": 50, "kwh": 500, "renewable_pct": 92}])
    assert r["renewable_pct"] == 92.0
    assert r["green"]
