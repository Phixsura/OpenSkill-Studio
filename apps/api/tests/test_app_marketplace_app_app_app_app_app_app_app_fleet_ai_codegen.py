from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_codegen import fleet_ai_codegen
def test_cg():
    r = fleet_ai_codegen([{"active": True, "completions_24h": 1000000, "acceptance_pct": 35, "lines_generated_24h": 500000}])
    assert r["completions_24h"] == 1000000
    assert r["acceptance_rate"] == 35.0
