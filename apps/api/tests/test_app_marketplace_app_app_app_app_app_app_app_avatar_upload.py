from app.services.app_marketplace_app_app_app_app_app_app_app_avatar_upload import validate_avatar, generate_avatar_url

def test_valid():
    r = validate_avatar(filename="photo.png", size_bytes=500000, width=256, height=256)
    assert r["valid"]
    assert r["extension"] == ".png"

def test_invalid_type():
    r = validate_avatar(filename="doc.pdf", size_bytes=1000)
    assert not r["valid"]
    assert any("not allowed" in e for e in r["errors"])

def test_too_large():
    r = validate_avatar(filename="huge.jpg", size_bytes=10 * 1024 * 1024)
    assert not r["valid"]

def test_url():
    url = generate_avatar_url("user123")
    assert url.startswith("https://cdn.openskill.io/avatars/")
    assert url.endswith(".png")
