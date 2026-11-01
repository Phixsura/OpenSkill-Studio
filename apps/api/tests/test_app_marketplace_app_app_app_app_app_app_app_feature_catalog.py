from app.services.app_marketplace_app_app_app_app_app_app_app_feature_catalog import list_features, feature_summary

def test_list():
    r = list_features()
    assert r["total"] == 10
    r2 = list_features(module="security")
    assert r2["total"] == 2

def test_summary():
    r = feature_summary()
    assert r["ga"] == 9
    assert r["beta"] == 1
    assert r["ga_pct"] == 90
