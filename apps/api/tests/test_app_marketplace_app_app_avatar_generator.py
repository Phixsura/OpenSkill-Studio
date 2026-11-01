from app.services.app_marketplace_app_app_avatar_generator import generate_avatar, generate_app_icon

def test_avatar():
    r = generate_avatar(name="Alice Developer", size=48)
    assert r["initials"] == "AD"
    assert r["size"] == 48
    assert r["bg_color"].startswith("#")
    assert r["font_size"] == 24

def test_single_name():
    r = generate_avatar(name="Alice")
    assert r["initials"] == "A"

def test_app_icon():
    r = generate_app_icon(app_name="Auth SDK", category="security")
    assert r["category_icon"] == "🔒"
    assert r["has_category_icon"]

def test_app_icon_no_cat():
    r = generate_app_icon(app_name="MyApp")
    assert not r["has_category_icon"]
