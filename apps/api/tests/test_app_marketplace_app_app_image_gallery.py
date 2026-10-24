from app.services.app_marketplace_app_app_image_gallery import build_image_gallery

def test_gallery():
    imgs = [
        {"src": "https://example.com/a.png", "alt": "Screenshot 1", "caption": "Dashboard"},
        {"src": "https://example.com/b.png", "alt": "Screenshot 2"},
    ]
    r = build_image_gallery(images=imgs)
    assert r["count"] == 2
    assert r["images"][0]["caption"] == "Dashboard"

def test_bad_scheme():
    r = build_image_gallery(images=[{"src": "javascript:alert(1)", "alt": "x"}])
    assert r["count"] == 0

def test_xss():
    r = build_image_gallery(images=[{"src": "https://x.com/a.png", "alt": "<script>", "caption": "<b>hi</b>"}])
    assert "<script>" not in r["images"][0]["alt"]
    assert "<b>" not in r["images"][0]["caption"]
