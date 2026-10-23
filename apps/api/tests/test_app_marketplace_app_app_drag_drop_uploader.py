from app.services.app_marketplace_app_app_drag_drop_uploader import validate_upload, build_upload_summary

def test_valid_file():
    r = validate_upload(filename="logo.png", size_bytes=1024 * 500)
    assert r["valid"]
    assert r["extension"] == ".png"

def test_invalid_ext():
    r = validate_upload(filename="script.exe", size_bytes=100)
    assert not r["valid"]

def test_too_large():
    r = validate_upload(filename="big.zip", size_bytes=100 * 1024 * 1024)
    assert not r["valid"]
    assert "too large" in r["errors"][0]

def test_summary():
    files = [
        {"name": "a.png", "size_bytes": 1000},
        {"name": "b.exe", "size_bytes": 500},
        {"name": "c.pdf", "size_bytes": 2000},
    ]
    r = build_upload_summary(files=files)
    assert r["total_files"] == 3
    assert r["valid_files"] == 2
    assert r["rejected_files"] == 1
