from app.services.app_marketplace_app_app_string_utils import slugify, truncate, word_count, highlight_matches

def test_slugify():
    assert slugify(text="Hello World!") == "hello-world"
    assert slugify(text="  My Cool App  ") == "my-cool-app"
    assert slugify(text="Already-Slug") == "already-slug"

def test_truncate():
    assert truncate(text="Short") == "Short"
    assert truncate(text="This is a longer text that should be truncated", max_length=20) == "This is a longer..."

def test_word_count():
    r = word_count(text="Hello world. This is a test.")
    assert r["words"] == 6
    assert r["sentences"] == 2
    assert r["reading_time_min"] == 1

def test_highlight():
    r = highlight_matches(text="Hello World", query="world")
    assert "<mark>" in r
    assert "World</mark>" in r
