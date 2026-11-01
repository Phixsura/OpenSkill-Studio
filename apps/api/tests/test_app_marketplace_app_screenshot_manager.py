from app.services.app_marketplace_app_screenshot_manager import validate_screenshot, reorder_screenshots

def test_valid():
    r = validate_screenshot(filename="screen.png", file_size_bytes=2_000_000, width=1280, height=720)
    assert r["valid"]

def test_invalid_format():
    r = validate_screenshot(filename="screen.bmp", file_size_bytes=1000, width=1280, height=720)
    assert not r["valid"]
    assert any("format" in e.lower() for e in r["errors"])

def test_too_large():
    r = validate_screenshot(filename="screen.png", file_size_bytes=10_000_000, width=1280, height=720)
    assert not r["valid"]

def test_reorder():
    shots = [{"id": "s1", "url": "a.png"}, {"id": "s2", "url": "b.png"}]
    r = reorder_screenshots(screenshots=shots, new_order=["s2", "s1"])
    assert r["success"]
    assert r["screenshots"][0]["id"] == "s2"
    assert r["screenshots"][0]["position"] == 0
