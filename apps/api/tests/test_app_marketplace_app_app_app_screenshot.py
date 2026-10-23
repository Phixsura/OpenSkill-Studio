from app.services.app_marketplace_app_app_app_screenshot import validate_screenshot, build_screenshot_gallery

def test_valid():
    r = validate_screenshot(url="https://cdn.example.com/shot1.png", alt_text="Dashboard")
    assert r["valid"]
    assert r["format"] == "png"

def test_invalid_format():
    r = validate_screenshot(url="https://cdn.example.com/doc.pdf")
    assert not r["valid"]

def test_gallery():
    shots = [
        {"url": "https://a.com/1.png", "alt_text": "A", "order": 2, "valid": True, "format": "png"},
        {"url": "https://a.com/2.jpg", "alt_text": "B", "order": 1, "valid": True, "format": "jpg"},
    ]
    r = build_screenshot_gallery(screenshots=shots)
    assert r["total"] == 2
    assert r["meets_minimum"]
    assert r["screenshots"][0]["order"] == 1  # sorted
