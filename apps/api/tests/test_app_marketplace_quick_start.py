from app.services.app_marketplace_quick_start import get_quick_start, get_step

def test_quick_start():
    qs = get_quick_start()
    assert len(qs["steps"]) == 6
    assert qs["total_time_min"] == 5

def test_step():
    s = get_step(step_number=3)
    assert "create" in s["command"]

def test_missing():
    assert get_step(step_number=99) is None
