from app.services.app_marketplace_app_app_tag_input import validate_tag, validate_tags, suggest_tags

def test_valid_tag():
    assert validate_tag(tag="developer-tools")["valid"]

def test_invalid_tag():
    assert not validate_tag(tag="BAD TAG!")["valid"]

def test_validate_list():
    r = validate_tags(tags=["api", "tools", "api"])  # duplicate
    assert r["duplicates_removed"] == 1
    assert len(r["tags"]) == 2

def test_suggest():
    r = suggest_tags(query="auto")
    assert "automation" in r
