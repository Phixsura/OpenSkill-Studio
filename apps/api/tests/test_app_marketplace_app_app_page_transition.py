from app.services.app_marketplace_app_app_page_transition import get_transition, get_all_transitions

def test_fade():
    r = get_transition(name="fade")
    assert r["duration_ms"] == 200
    assert r["easing"] == "ease-in-out"

def test_slide():
    r = get_transition(name="slide_left")
    assert r["duration_ms"] == 300

def test_all():
    r = get_all_transitions()
    assert r["total"] == 5
    assert r["default"] == "fade"
