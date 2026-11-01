from app.services.app_marketplace_app_app_app_app_app_app_app_feature_toggle import FeatureToggleRouter

def test_toggle():
    r = FeatureToggleRouter()
    r.create("new_ui", enabled=True, rollout_pct=50, segments=["beta"])
    e1 = r.evaluate("new_ui", segment="beta")
    assert e1["enabled"]
    assert e1["reason"] == "segment_match"
    e2 = r.evaluate("new_ui", user_id="user_abc")
    # Either in rollout or not, but reason should be valid
    assert e2["reason"] in ("rollout", "not_in_rollout")
    r.create("old_feature", enabled=False)
    e3 = r.evaluate("old_feature")
    assert not e3["enabled"]
    assert e3["reason"] == "globally_disabled"

def test_not_found():
    r = FeatureToggleRouter()
    e = r.evaluate("nope")
    assert not e["enabled"]
    assert e["reason"] == "toggle_not_found"
