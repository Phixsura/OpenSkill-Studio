from app.services.app_getting_started import get_guide, get_current_step

def test_guide_count():
    assert len(get_guide()) == 6

def test_current_step_first():
    s = get_current_step(set())
    assert s["step"] == 1

def test_current_step_mid():
    s = get_current_step({1, 2, 3})
    assert s["step"] == 4

def test_current_step_done():
    assert get_current_step({1, 2, 3, 4, 5, 6}) is None
