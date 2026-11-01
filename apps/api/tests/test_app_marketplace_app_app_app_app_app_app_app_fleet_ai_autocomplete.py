from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_autocomplete import fleet_ai_autocomplete
def test_ac():
    r = fleet_ai_autocomplete([{"active": True, "completions_24h": 50000000, "acceptance_pct": 42, "latency_ms": 50}])
    assert r["completions_24h"] == 50000000
    assert r["helpful"]
