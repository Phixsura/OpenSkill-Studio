from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_guard import fleet_ai_guardrails
def test_guard():
    r = fleet_ai_guardrails([{"active": True, "blocked_24h": 500, "checks_24h": 100000}])
    assert r["block_rate_pct"] == 0.5
