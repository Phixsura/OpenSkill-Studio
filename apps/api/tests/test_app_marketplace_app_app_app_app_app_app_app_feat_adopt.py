from app.services.app_marketplace_app_app_app_app_app_app_app_feat_adopt import track_adoption, adoption_funnel

def test_adoption():
    r = track_adoption([
        {"feature": "dark_mode", "user_id": "u1"},
        {"feature": "dark_mode", "user_id": "u2"},
        {"feature": "export", "user_id": "u1"},
    ], total_users=10)
    assert r["features"][0]["feature"] == "dark_mode"
    assert r["features"][0]["adoption_pct"] == 20.0

def test_funnel():
    r = adoption_funnel([
        {"name": "signup", "count": 1000},
        {"name": "onboarding", "count": 800},
        {"name": "first_action", "count": 500},
    ])
    assert r["completion_pct"] == 50.0
    assert r["steps"][1]["drop_off_pct"] == 20.0
