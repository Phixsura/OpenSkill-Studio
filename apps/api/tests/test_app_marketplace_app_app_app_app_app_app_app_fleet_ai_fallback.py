from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_fallback import fleet_ai_fallback
def test_fb():
    r = fleet_ai_fallback([{"active": True, "fallbacks_24h": 500, "primary_success_pct": 95}])
    assert r["fallbacks_24h"] == 500
    assert r["resilient"]
