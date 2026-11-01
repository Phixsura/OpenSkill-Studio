from app.services.app_marketplace_app_file_upload_validator import validate_upload

def test_valid_image():
    r = validate_upload(filename="logo.png", size_bytes=500_000, category="image")
    assert r["valid"]

def test_wrong_type():
    r = validate_upload(filename="hack.exe", size_bytes=1000, category="image")
    assert not r["valid"]
    assert any("not allowed" in e for e in r["errors"])

def test_too_large():
    r = validate_upload(filename="big.png", size_bytes=10_000_000, category="image")
    assert not r["valid"]
    assert any("too large" in e.lower() for e in r["errors"])

def test_bad_filename():
    r = validate_upload(filename="file<script>.png", size_bytes=1000, category="image")
    assert not r["valid"]

def test_invalid_cat():
    r = validate_upload(filename="x.bin", size_bytes=100, category="executable")
    assert not r["valid"]
