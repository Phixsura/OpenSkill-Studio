from app.services.app_marketplace_app_developer_app_feature_usage_tracking import track_feature_usage, compute_feature_adoption, identify_unused_features, compute_feature_stickiness

def test_track():
    r = track_feature_usage(app_id="a1", feature="dark_mode", user_id="u1")
    assert r["action"] == "used"

def test_adoption():
    events = [{"feature": "search", "user_id": "u1"}, {"feature": "search", "user_id": "u2"},
              {"feature": "export", "user_id": "u1"}]
    r = compute_feature_adoption(events=events, total_users=10)
    assert r[0]["feature"] == "search"
    assert r[0]["adoption_pct"] == 20.0

def test_unused():
    r = identify_unused_features(all_features=["a", "b", "c", "d"], used_features=["a", "c"])
    assert r == ["b", "d"]

def test_stickiness():
    r = compute_feature_stickiness(daily_users={"search": 80}, monthly_users={"search": 200})
    assert r["search"]["stickiness"] == 40.0
