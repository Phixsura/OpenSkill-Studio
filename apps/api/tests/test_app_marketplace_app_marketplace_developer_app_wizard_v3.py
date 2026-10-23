from app.services.app_marketplace_app_marketplace_developer_app_wizard_v3 import get_wizard_steps, compute_wizard_progress, validate_wizard_step

def test_steps():
    s = get_wizard_steps()
    assert len(s) == 6

def test_progress():
    r = compute_wizard_progress(completed_steps=["basics", "manifest", "review"])
    assert r["required_complete"]
    assert r["can_submit"]

def test_not_ready():
    r = compute_wizard_progress(completed_steps=["basics"])
    assert not r["can_submit"]
    assert r["next_step"] == "manifest"

def test_validate_ok():
    r = validate_wizard_step(step_key="basics", data={"name": "MyApp", "slug": "my-app", "category": "connector"})
    assert r["valid"]

def test_validate_fail():
    r = validate_wizard_step(step_key="basics", data={"name": "AB"})
    assert not r["valid"]
    assert len(r["errors"]) >= 2
