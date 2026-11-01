from app.services.app_marketplace_app_app_feature_card import build_feature_cards

def test_cards():
    features = [
        {"title": "Easy SDK", "description": "Get started fast", "icon": "🚀", "category": "development"},
        {"title": "Real-time", "description": "Live updates", "icon": "⚡", "category": "infrastructure"},
    ]
    r = build_feature_cards(features=features)
    assert r["total"] == 2
    assert len(r["categories"]) == 2
    assert r["cards"][0]["title"] == "Easy SDK"

def test_xss():
    r = build_feature_cards(features=[{"title": "<script>x</script>"}])
    assert "<script>" not in r["cards"][0]["title"]
