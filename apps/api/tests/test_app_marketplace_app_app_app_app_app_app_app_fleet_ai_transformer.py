from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_transformer import fleet_ai_transformer
def test_tf():
    r = fleet_ai_transformer([{"active": True, "models": 50, "speedup_x": 3.5, "memory_saved_pct": 40}])
    assert r["speedup_x"] == 3.5
    assert r["optimized"]
