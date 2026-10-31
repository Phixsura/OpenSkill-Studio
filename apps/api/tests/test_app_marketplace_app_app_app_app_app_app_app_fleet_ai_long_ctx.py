from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_long_ctx import fleet_ai_long_context
def test_lc():
    r = fleet_ai_long_context([{"active": True, "max_tokens": 1000000, "utilization_pct": 72, "requests_24h": 500000}])
    assert r["max_tokens"] == 1000000
    assert r["extended"]
