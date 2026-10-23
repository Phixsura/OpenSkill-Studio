from app.services.app_marketplace_app_app_color_picker import validate_color, get_presets

def test_preset():
    r = validate_color("blue")
    assert r["valid"]
    assert r["hex"] == "#3B82F6"
    assert r["source"] == "preset"

def test_custom_hex():
    r = validate_color("#FF5500")
    assert r["valid"]
    assert r["hex"] == "#FF5500"
    assert r["source"] == "custom"

def test_invalid():
    r = validate_color("nope")
    assert not r["valid"]
    assert "error" in r

def test_presets_list():
    p = get_presets()
    assert len(p) == 8
    assert any(x["name"] == "teal" for x in p)
