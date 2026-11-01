from app.services.app_marketplace_app_app_app_app_app_app_app_feat_usage import FeatureUsageTracker

def test_track():
    ft = FeatureUsageTracker()
    ft.track("dark_mode", "u1")
    ft.track("dark_mode", "u2")
    ft.track("export", "u1")
    top = ft.top_features()
    assert top[0]["feature"] == "dark_mode"
    assert top[0]["unique_users"] == 2

def test_unused():
    ft = FeatureUsageTracker()
    ft.track("a", "u1")
    unused = ft.unused_features(["a", "b", "c"])
    assert unused == ["b", "c"]
    assert ft.stats()["features_used"] == 1
