from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_memory import fleet_ai_memory
def test_aim():
    r = fleet_ai_memory([{"active": True, "memories": 10000000, "retrievals_24h": 5000000}])
    assert r["memories"] == 10000000
    assert r["all_active"]
