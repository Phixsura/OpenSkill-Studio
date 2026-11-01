"""Developer onboarding tests."""
import pytest
from app.services.app_developer_onboarding import get_onboarding_progress, ONBOARDING_STEPS

def test_empty_progress():
    p = get_onboarding_progress(set())
    assert p["completed_steps"] == 0
    assert p["progress_pct"] == 0
    assert p["required_complete"] is False
    assert p["next_step"]["key"] == "create_account"

def test_partial_progress():
    p = get_onboarding_progress({"create_account", "create_app"})
    assert p["completed_steps"] == 2
    assert p["progress_pct"] > 0

def test_all_required_complete():
    required = {s["key"] for s in ONBOARDING_STEPS if s["required"]}
    p = get_onboarding_progress(required)
    assert p["required_complete"] is True

def test_full_completion():
    all_keys = {s["key"] for s in ONBOARDING_STEPS}
    p = get_onboarding_progress(all_keys)
    assert p["progress_pct"] == 100
    assert p["next_step"] is None

def test_steps_have_completed_flag():
    p = get_onboarding_progress({"create_account"})
    steps = p["steps"]
    assert steps[0]["completed"] is True
    assert steps[1]["completed"] is False

def test_step_count():
    assert len(ONBOARDING_STEPS) >= 5
