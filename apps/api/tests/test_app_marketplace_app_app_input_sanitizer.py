from app.services.app_marketplace_app_app_input_sanitizer import sanitize_text, sanitize_url

def test_basic():
    r = sanitize_text(text="Hello world")
    assert r["sanitized"] == "Hello world"
    assert not r["modifications"]

def test_xss():
    r = sanitize_text(text='<script>alert("xss")</script>')
    assert "<script>" not in r["sanitized"]

def test_null_bytes():
    r = sanitize_text(text="hello\x00world")
    assert "\x00" not in r["sanitized"]
    assert r["modifications"]

def test_truncation():
    r = sanitize_text(text="a" * 200, max_length=100)
    assert r["truncated"]
    assert r["sanitized_length"] == 100

def test_markdown():
    r = sanitize_text(text='**bold** <script>alert(1)</script>', allow_markdown=True)
    assert "**bold**" in r["sanitized"]
    assert "<script>" not in r["sanitized"]

def test_safe_url():
    r = sanitize_url(url="https://example.com")
    assert r["safe"]

def test_unsafe_url():
    r = sanitize_url(url="javascript:alert(1)")
    assert not r["safe"]
    assert r["url"] == ""
