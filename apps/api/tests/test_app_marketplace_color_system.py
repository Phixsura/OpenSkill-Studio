from app.services.app_marketplace_color_system import get_status_color, get_color_palette, generate_css_custom_properties

def test_published():
    c = get_status_color(status="published")
    assert c["color_key"] == "success"
    assert c["bg"].startswith("#")

def test_draft():
    c = get_status_color(status="draft")
    assert c["color_key"] == "neutral"

def test_unknown():
    c = get_status_color(status="weird")
    assert c["color_key"] == "neutral"

def test_palette():
    p = get_color_palette()
    assert "primary" in p
    assert "500" in p["primary"]

def test_css():
    props = generate_css_custom_properties()
    assert "--color-primary-500" in props
    assert props["--color-primary-500"] == "#3b82f6"
