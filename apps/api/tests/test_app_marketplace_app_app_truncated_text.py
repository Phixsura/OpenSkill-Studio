from app.services.app_marketplace_app_app_truncated_text import truncate_text, truncate_middle

def test_short():
    r = truncate_text(text="Hello", max_length=100)
    assert not r["truncated"]
    assert r["text"] == "Hello"

def test_long():
    r = truncate_text(text="This is a very long description that should be truncated", max_length=30)
    assert r["truncated"]
    assert r["text"].endswith("...")
    assert len(r["text"]) <= 30

def test_xss():
    r = truncate_text(text="<script>alert(1)</script>", max_length=100)
    assert "<script>" not in r["text"]

def test_middle():
    r = truncate_middle(text="very-long-file-path/to/some/deeply/nested/file.tsx", max_length=30)
    assert r["truncated"]
    assert "..." in r["text"]
    assert len(r["text"]) <= 30
