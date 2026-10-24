from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_classify import fleet_ai_classify
def test_cls():
    r = fleet_ai_classify([{"active": True, "classifications_24h": 5000000, "accuracy_pct": 97}])
    assert r["classifications_24h"] == 5000000
    assert r["high_accuracy"]
