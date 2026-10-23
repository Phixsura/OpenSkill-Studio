from app.services.app_marketplace_app_app_banner_carousel import build_carousel

def test_carousel():
    banners = [
        {"title": "New Feature!", "subtitle": "Dark mode", "cta_label": "Try it", "cta_url": "/settings"},
        {"title": "SDK v3", "subtitle": "Now available", "bg_gradient": "from-green-500 to-teal-600"},
    ]
    r = build_carousel(banners=banners)
    assert r["total"] == 2
    assert r["auto_rotate"]
    assert r["banners"][0]["title"] == "New Feature!"

def test_single():
    r = build_carousel(banners=[{"title": "Hello"}])
    assert not r["auto_rotate"]

def test_xss():
    r = build_carousel(banners=[{"title": "<script>xss</script>"}])
    assert "<script>" not in r["banners"][0]["title"]
