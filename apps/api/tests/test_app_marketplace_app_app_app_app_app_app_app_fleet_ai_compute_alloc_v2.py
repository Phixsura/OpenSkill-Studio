from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_compute_alloc_v2 import fleet_ai_compute_allocator_v2
def test_cav2():
    r = fleet_ai_compute_allocator_v2([{"active": True, "gpus": 5000, "allocated": 4500, "cost_saved_pct": 30}])
    assert r["efficiency"] == 90.0
    assert r["optimal"]
