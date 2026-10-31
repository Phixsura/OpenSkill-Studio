from app.services.app_marketplace_developer_getting_started import get_tutorial, get_tutorial_step, compute_tutorial_progress

def test_tutorial():
    t = get_tutorial()
    assert t["total_steps"] == 5
    assert t["total_duration_min"] == 45

def test_step():
    s = get_tutorial_step(step_number=3)
    assert s["title"] == "Add Your Logic"

def test_step_not_found():
    assert get_tutorial_step(step_number=99) is None

def test_progress():
    p = compute_tutorial_progress(completed_steps=[1, 2])
    assert p["completed"] == 2
    assert p["pct"] == 40
    assert p["next_step"] == 3
    assert not p["all_done"]

def test_complete():
    p = compute_tutorial_progress(completed_steps=[1, 2, 3, 4, 5])
    assert p["all_done"]
    assert p["next_step"] is None
