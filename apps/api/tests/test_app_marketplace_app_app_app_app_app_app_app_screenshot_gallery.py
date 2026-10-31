from app.services.app_marketplace_app_app_app_app_app_app_app_screenshot_gallery import build_screenshot_gallery, validate_screenshots

def test_gallery():
    r = build_screenshot_gallery([
        {"url": "https://cdn.example.com/1.png", "alt": "Dashboard", "caption": "Main view"},
        {"url": "https://cdn.example.com/2.png", "alt": "Settings"},
        {"url": "http://insecure.com/3.png", "alt": "Bad"},  # skipped
    ], app_name="MyApp")
    assert r["count"] == 2
    assert r["screenshots"][0]["alt"] == "Dashboard"

def test_validate():
    r = validate_screenshots([
        {"url": "https://cdn.example.com/1.png", "alt": "OK"},
        {"url": "http://bad.com/2.png", "alt": ""},
    ])
    assert not r["valid"]
    assert len(r["errors"]) == 2  # non-https + missing alt
