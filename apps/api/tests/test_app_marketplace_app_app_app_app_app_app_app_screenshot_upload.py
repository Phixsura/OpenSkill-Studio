from app.services.app_marketplace_app_app_app_app_app_app_app_screenshot_upload import validate_screenshot, reorder_screenshots

def test_valid():
    r = validate_screenshot(filename="screen.png", size_bytes=2000000, width=1920, height=1080)
    assert r["valid"]
    assert r["dimensions"] == "1920x1080"

def test_invalid():
    r = validate_screenshot(filename="small.gif", size_bytes=100, width=100, height=100)
    assert not r["valid"]
    assert len(r["errors"]) >= 2  # format + dimensions

def test_reorder():
    r = reorder_screenshots(["a", "b", "c", "d"], from_idx=0, to_idx=2)
    assert r == ["b", "c", "a", "d"]
