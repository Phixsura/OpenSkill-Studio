from app.services.app_marketplace_app_app_app_app_app_app_app_file_uploader import validate_upload

def test_valid():
    r = validate_upload(filename="logo.png", size_bytes=500000, category="image")
    assert r["valid"]
    assert r["extension"] == ".png"
    assert "KB" in r["size_display"]

def test_too_large():
    r = validate_upload(filename="big.png", size_bytes=15 * 1024 * 1024, category="image")
    assert not r["valid"]
    assert "too large" in r["error"]

def test_wrong_type():
    r = validate_upload(filename="script.exe", size_bytes=1000, category="image")
    assert not r["valid"]
    assert "not allowed" in r["error"]
