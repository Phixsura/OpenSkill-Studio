from app.services.app_marketplace_app_app_app_app_app_app_app_feature_compare import build_comparison, find_unique_features

def test_compare():
    products = [
        {"name": "Basic", "features": {"sso": False, "api": True, "webhooks": False, "analytics": True}},
        {"name": "Pro", "features": {"sso": True, "api": True, "webhooks": True, "analytics": True}},
    ]
    features = ["sso", "api", "webhooks", "analytics"]
    r = build_comparison(products, features)
    assert r["best_match"] == "Pro"
    assert r["scores"]["Pro"]["total"] == 4
    assert r["scores"]["Basic"]["total"] == 2
    assert r["matrix"][0]["feature"] == "sso"
    assert r["matrix"][0]["values"]["Pro"] is True
    assert r["matrix"][0]["values"]["Basic"] is False

def test_unique():
    products = [
        {"name": "A", "features": {"x": True, "y": True}},
        {"name": "B", "features": {"x": True, "z": True}},
    ]
    r = find_unique_features(products, ["x", "y", "z"])
    assert "y" in r["unique_features"]["A"]
    assert "z" in r["unique_features"]["B"]
