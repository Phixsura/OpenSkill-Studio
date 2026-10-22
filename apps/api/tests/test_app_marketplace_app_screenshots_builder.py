from app.services.app_marketplace_app_screenshots_builder import build_screenshots

def test_with():
    s = build_screenshots([{"url": "img1.png"}, {"url": "img2.png"}])
    assert s["count"] == 2
    assert s["has_screenshots"] is True

def test_empty():
    s = build_screenshots([])
    assert s["has_screenshots"] is False
