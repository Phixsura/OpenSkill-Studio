from app.services.app_icon_validator import validate_icon_url

def test_valid_png():
    assert validate_icon_url("https://cdn.example.com/icon.png") == []

def test_valid_svg():
    assert validate_icon_url("https://cdn.example.com/icon.svg") == []

def test_none_ok():
    assert validate_icon_url(None) == []

def test_bad_ext():
    assert len(validate_icon_url("https://x.com/file.exe")) > 0

def test_bad_scheme():
    assert len(validate_icon_url("ftp://x.com/icon.png")) > 0

def test_too_long():
    assert len(validate_icon_url("https://x.com/" + "a" * 500 + ".png")) > 0
