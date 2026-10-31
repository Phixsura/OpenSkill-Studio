from app.services.app_marketplace_app_app_feature_toggle import evaluate_toggle, bulk_evaluate

def test_full_rollout():
    r = evaluate_toggle(feature="dark_mode", user_id="u1", rollout_pct=100)
    assert r["enabled"]
    assert r["reason"] == "full_rollout"

def test_override():
    r = evaluate_toggle(feature="beta", user_id="u1", overrides={"u1": True})
    assert r["enabled"]
    assert r["reason"] == "override"

def test_deterministic():
    r1 = evaluate_toggle(feature="f", user_id="u1", rollout_pct=50)
    r2 = evaluate_toggle(feature="f", user_id="u1", rollout_pct=50)
    assert r1["enabled"] == r2["enabled"]

def test_bulk():
    features = [{"name": "a", "rollout_pct": 100}, {"name": "b", "rollout_pct": 0}]
    r = bulk_evaluate(features=features, user_id="u1")
    assert r["toggles"]["a"]
    assert not r["toggles"]["b"]
    assert r["enabled"] == 1
