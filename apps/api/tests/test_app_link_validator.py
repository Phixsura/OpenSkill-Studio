from app.services.app_link_validator import validate_homepage_url, validate_privacy_url, validate_all_links

def test_valid_homepage():
    assert validate_homepage_url("https://myapp.com") == []

def test_http_rejected():
    assert len(validate_homepage_url("http://myapp.com")) > 0

def test_none_ok():
    assert validate_homepage_url(None) == []

def test_valid_privacy():
    assert validate_privacy_url("https://myapp.com/privacy") == []

def test_all_valid():
    assert validate_all_links(homepage="https://x.com", privacy="https://x.com/p") == []

def test_all_mixed():
    errors = validate_all_links(homepage="http://x.com", privacy="https://x.com/p")
    assert len(errors) > 0
