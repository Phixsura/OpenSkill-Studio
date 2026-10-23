from app.services.app_marketplace_app_color_palette import validate_color, generate_palette, check_contrast

def test_valid_color():
    r = validate_color(color="#3b82f6")
    assert r["valid"]
    assert r["rgb"]["r"] == 59

def test_invalid():
    r = validate_color(color="not-a-color")
    assert not r["valid"]

def test_palette():
    r = generate_palette(primary="#3b82f6", count=5)
    assert len(r["palette"]) == 5
    assert r["primary"] == "#3b82f6"

def test_contrast():
    r = check_contrast(fg="#000000", bg="#ffffff")
    assert r["ratio"] >= 20
    assert r["aa_normal"]
    assert r["aaa_normal"]
