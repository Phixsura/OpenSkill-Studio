from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_inf_cache import fleet_ai_inference_cache
def test_ic():
    r = fleet_ai_inference_cache([{"active": True, "entries": 10000000, "hit_rate": 65, "cost_saved": 5000}])
    assert r["hit_rate"] == 65.0
    assert r["valuable"]
