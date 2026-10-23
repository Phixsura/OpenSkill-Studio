from app.services.app_marketplace_animation_config import get_animation, get_reduced_motion_config, should_animate

def test_get():
    a = get_animation(name="modal_open")
    assert a["duration_ms"] == 200
    assert a["type"] == "scale-fade"

def test_unknown():
    assert get_animation(name="nope") is None

def test_reduced_motion():
    r = get_reduced_motion_config()
    assert all(v["duration_ms"] == 0 for v in r.values())

def test_should_animate():
    assert should_animate(prefers_reduced_motion=False)
    assert not should_animate(prefers_reduced_motion=True)
