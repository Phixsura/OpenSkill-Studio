from app.services.app_marketplace_content_policy import validate_listing_content, sanitize_html

def test_valid():
    r = validate_listing_content(name="My App", description="A great tool", tags=["utility"])
    assert r["compliant"]

def test_forbidden_word():
    r = validate_listing_content(name="Hack Tool", description="D", tags=[])
    assert not r["compliant"]

def test_external_link():
    r = validate_listing_content(name="App", description="Visit https://evil.com", tags=[])
    assert not r["compliant"]

def test_too_many_tags():
    r = validate_listing_content(name="App", description="D", tags=[f"t{i}" for i in range(15)])
    assert not r["compliant"]

def test_sanitize():
    r = sanitize_html(content='Hello <script>alert("xss")</script> World')
    assert "<script>" not in r
    assert "Hello" in r

def test_sanitize_event():
    r = sanitize_html(content='<div onclick="alert(1)">Click</div>')
    assert "onclick" not in r
