from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_res_alloc import fleet_ai_resource_allocator
def test_ra():
    r = fleet_ai_resource_allocator([{"active": True, "gpus": 1000, "allocated": 950, "waste_pct": 5}])
    assert r["allocated"] == 950
    assert r["efficient"]
