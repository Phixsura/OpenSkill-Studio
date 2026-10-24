from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_ctx_win import fleet_ai_context_window
def test_cw():
    r = fleet_ai_context_window([{"active": True, "max_tokens": 1000000, "usage_pct": 65, "overflows": 0}])
    assert r["max_tokens"] == 1000000
    assert r["optimized"]
