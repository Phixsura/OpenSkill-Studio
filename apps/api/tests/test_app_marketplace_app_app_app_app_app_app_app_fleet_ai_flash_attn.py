from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_flash_attn import fleet_ai_flash_attention
def test_fa():
    r = fleet_ai_flash_attention([{"active": True, "speedup_x": 3.5, "memory_saved_pct": 60, "max_seq_len": 1000000}])
    assert r["speedup_x"] == 3.5
    assert r["optimized"]
