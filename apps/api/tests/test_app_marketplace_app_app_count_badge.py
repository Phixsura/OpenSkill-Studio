from app.services.app_marketplace_app_app_count_badge import build_count_badge

def test_small():
    r = build_count_badge(count=3)
    assert r["display"] == "3"
    assert r["size"] == "sm"
    assert r["visible"]

def test_over_max():
    r = build_count_badge(count=150, max_display=99)
    assert r["display"] == "99+"
    assert r["size"] == "lg"

def test_zero():
    r = build_count_badge(count=0)
    assert not r["visible"]
    assert r["urgency"] == "low"
