from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_sentiment import fleet_ai_sentiment
def test_sent():
    r = fleet_ai_sentiment([{"active": True, "analyses_24h": 3000000, "positive_pct": 72}])
    assert r["analyses_24h"] == 3000000
    assert r["all_active"]
