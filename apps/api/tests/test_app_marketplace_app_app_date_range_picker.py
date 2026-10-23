from app.services.app_marketplace_app_app_date_range_picker import build_date_range, list_presets

def test_preset():
    r = build_date_range(preset="last_7d")
    assert r["days"] == 8
    assert r["preset"] == "last_7d"

def test_custom():
    r = build_date_range(start="2026-01-01", end="2026-01-31")
    assert r["days"] == 31
    assert r["preset"] is None

def test_default():
    r = build_date_range()
    assert r["preset"] == "today"

def test_presets():
    p = list_presets()
    assert len(p) == 6
    assert any(x["id"] == "last_30d" for x in p)
