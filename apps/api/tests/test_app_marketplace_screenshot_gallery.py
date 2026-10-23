from app.services.app_marketplace_screenshot_gallery import build_screenshot_gallery, validate_screenshot

def test_gallery():
    shots = [{"url": f"s{i}.png"} for i in range(15)]
    g = build_screenshot_gallery(screenshots=shots, max_display=10)
    assert g["count"] == 10
    assert g["has_more"]
    assert g["items"][0]["alt"] == "Screenshot 1"

def test_validate_ok():
    r = validate_screenshot(width=1280, height=720, size_bytes=500000, format="png")
    assert r["valid"]

def test_validate_too_small():
    r = validate_screenshot(width=320, height=240, size_bytes=1000, format="png")
    assert not r["valid"]

def test_validate_bad_format():
    r = validate_screenshot(width=1280, height=720, size_bytes=1000, format="gif")
    assert not r["valid"]
