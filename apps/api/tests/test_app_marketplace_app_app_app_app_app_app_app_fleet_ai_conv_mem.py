from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_conv_mem import fleet_ai_conv_memory
def test_cm():
    r = fleet_ai_conv_memory([{"active": True, "conversations": 10000000, "messages": 100000000}])
    assert r["conversations"] == 10000000
    assert r["all_active"]
