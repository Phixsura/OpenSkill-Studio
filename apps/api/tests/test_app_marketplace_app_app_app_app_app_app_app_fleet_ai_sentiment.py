from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_sentiment import fleet_ai_sentiment
def test_sent():
    r = fleet_ai_sentiment([{"active": True, "analyzed_24h": 5000000, "accuracy": 94, "emotions": ["joy", "anger", "sadness", "fear", "surprise"]}])
    assert r["emotions"] == 5
    assert r["precise"]
