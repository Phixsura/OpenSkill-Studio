from app.services.app_marketplace_app_app_app_app_app_app_app_color_palette import generate_shades, check_contrast, hex_to_rgb

def test_shades():
    shades = generate_shades("#3B82F6", steps=5)
    assert len(shades) == 5
    assert shades[0]["shade"] == 500  # lightest
    assert shades[-1]["shade"] == 100  # darkest
    assert shades[0]["hex"].startswith("#")

def test_contrast():
    r = check_contrast("#000000", "#FFFFFF")
    assert r["ratio"] == 21.0
    assert r["aa_normal"]
    assert r["aaa_normal"]
    r2 = check_contrast("#777777", "#888888")
    assert not r2["aa_normal"]

def test_rgb():
    assert hex_to_rgb("#FF0000") == (255, 0, 0)
