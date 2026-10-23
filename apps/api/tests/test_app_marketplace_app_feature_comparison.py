from app.services.app_marketplace_app_feature_comparison import compare_features

def test_compare():
    items = [
        {"id": "a1", "name": "Basic", "features": ["auth", "api"]},
        {"id": "a2", "name": "Pro", "features": ["auth", "api", "analytics", "webhooks"]},
    ]
    features = ["auth", "api", "analytics", "webhooks", "sso"]
    r = compare_features(items=items, features=features)
    assert r["winner"]["name"] == "Pro"
    assert r["winner"]["feature_count"] == 4
    assert r["matrix"][0]["analytics"] is True
    assert r["matrix"][1]["analytics"] is False

def test_empty():
    r = compare_features(items=[], features=["x"])
    assert r["winner"] is None
