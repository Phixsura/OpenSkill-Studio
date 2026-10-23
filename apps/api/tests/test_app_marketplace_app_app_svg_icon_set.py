from app.services.app_marketplace_app_app_svg_icon_set import get_icon, list_icons

def test_get_icon():
    r = get_icon(name="home", size=20)
    assert "<svg" in r["svg"]
    assert r["size"] == 20

def test_unknown():
    r = get_icon(name="nonexistent")
    assert "error" in r

def test_list():
    icons = list_icons()
    assert len(icons) == 8
    assert any(i["name"] == "search" for i in icons)
