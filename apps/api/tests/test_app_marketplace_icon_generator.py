from app.services.app_marketplace_icon_generator import generate_placeholder_icon, validate_icon, get_icon_requirements

def test_placeholder():
    p = generate_placeholder_icon(app_name="SuperApp")
    assert p["initial"] == "S"
    assert p["bg_color"].startswith("#")

def test_deterministic():
    p1 = generate_placeholder_icon(app_name="Test")
    p2 = generate_placeholder_icon(app_name="Test")
    assert p1["bg_color"] == p2["bg_color"]

def test_validate_ok():
    r = validate_icon(width=256, height=256, format="png", size_bytes=50000)
    assert r["valid"]

def test_validate_not_square():
    r = validate_icon(width=256, height=128, format="png", size_bytes=50000)
    assert not r["valid"]

def test_validate_too_small():
    r = validate_icon(width=64, height=64, format="png", size_bytes=1000)
    assert not r["valid"]

def test_requirements():
    r = get_icon_requirements()
    assert r["recommended_size"] == 256
