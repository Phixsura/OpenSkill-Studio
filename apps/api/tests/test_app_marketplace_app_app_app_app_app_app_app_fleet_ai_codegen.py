from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_codegen import fleet_ai_codegen
def test_cg():
    r = fleet_ai_codegen([{"active": True, "completions_24h": 5000000, "acceptance_pct": 42, "languages": ["python", "typescript", "rust"]}])
    assert r["completions_24h"] == 5000000
    assert r["productive"]
