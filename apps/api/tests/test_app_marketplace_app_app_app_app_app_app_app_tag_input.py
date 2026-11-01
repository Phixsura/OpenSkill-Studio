from app.services.app_marketplace_app_app_app_app_app_app_app_tag_input import validate_tag, validate_tags, suggest_tags

def test_valid_tag():
    r = validate_tag("my-tag")
    assert r["valid"]
    r2 = validate_tag("My Tag")
    assert r2["valid"]
    assert r2["normalized"] == "my-tag"

def test_invalid_tag():
    r = validate_tag("-")
    assert not r["valid"]

def test_tags():
    r = validate_tags(["python", "api", "python", "web-app"])
    assert r["valid"]
    assert r["count"] == 3  # deduplicated
    assert r["duplicates_removed"] == 1

def test_suggest():
    available = ["python", "postgresql", "performance", "react", "redis"]
    r = suggest_tags("p", available)
    assert len(r) == 3
    assert all(s.startswith("p") for s in r)
