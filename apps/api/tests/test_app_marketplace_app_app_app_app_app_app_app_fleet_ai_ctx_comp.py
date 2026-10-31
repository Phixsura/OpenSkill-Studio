from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_ctx_comp import fleet_ai_context_compressor
def test_cc():
    r = fleet_ai_context_compressor([{"active": True, "compressions_24h": 5000000, "ratio": 4, "quality_pct": 98}])
    assert r["ratio"] == 4.0
    assert r["lossless"]
