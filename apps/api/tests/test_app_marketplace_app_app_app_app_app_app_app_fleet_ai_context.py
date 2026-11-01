from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_context import fleet_ai_context
def test_ctx():
    r = fleet_ai_context([{"active": True, "ctx_utilization_pct": 65, "truncations_24h": 100}])
    assert r["avg_utilization_pct"] == 65.0
    assert r["efficient"]
