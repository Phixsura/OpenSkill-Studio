from app.services.app_marketplace_app_screenshot_manager import validate_screenshot, reorder_screenshots, get_screenshot_requirements

def test_valid():
    r = validate_screenshot(filename="screen.png", size_bytes=1024 * 1024)
    assert r["valid"]

def test_invalid_format():
    r = validate_screenshot(filename="screen.gif", size_bytes=1000)
    assert not r["valid"]

def test_too_large():
    r = validate_screenshot(filename="big.png", size_bytes=10 * 1024 * 1024)
    assert not r["valid"]

def test_reorder():
    shots = [{"id": "a", "url": "a.png"}, {"id": "b", "url": "b.png"}, {"id": "c", "url": "c.png"}]
    r = reorder_screenshots(screenshots=shots, new_order=["c", "a", "b"])
    assert r[0]["id"] == "c"
    assert r[0]["position"] == 0

def test_requirements():
    r = get_screenshot_requirements()
    assert r["max_count"] == 10
    assert "png" in r["allowed_formats"]
