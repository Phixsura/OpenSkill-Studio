from app.services.app_marketplace_app_lifecycle_manager import get_lifecycle_stage, get_allowed_transitions, transition_app

def test_stage():
    s = get_lifecycle_stage(app={"status": "published"})
    assert s["stage"] == "published"
    assert s["progress_pct"] > 0

def test_transitions():
    t = get_allowed_transitions(current_stage="published")
    assert "maintenance" in t
    assert "draft" not in t

def test_transition_ok():
    r = transition_app(app={"status": "published"}, target_stage="deprecated")
    assert r["new_stage"] == "deprecated"

def test_transition_blocked():
    r = transition_app(app={"status": "draft"}, target_stage="published")
    assert r["error"]
