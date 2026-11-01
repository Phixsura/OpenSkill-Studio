from app.services.app_marketplace_tag_system import validate_tags, get_trending_tags, find_apps_by_tag, suggest_tags

def test_valid():
    r = validate_tags(tags=["webhook", "api", "oauth"])
    assert r["valid"]

def test_too_many():
    r = validate_tags(tags=[f"tag{i}" for i in range(15)], max_tags=10)
    assert not r["valid"]

def test_invalid_chars():
    r = validate_tags(tags=["good-tag", "bad tag!"])
    assert not r["valid"]

def test_trending():
    apps = [{"tags": ["webhook", "api"]}, {"tags": ["webhook"]}, {"tags": ["oauth"]}]
    t = get_trending_tags(apps=apps)
    assert t[0]["tag"] == "webhook"
    assert t[0]["count"] == 2

def test_find():
    apps = [{"name": "A", "tags": ["webhook"]}, {"name": "B", "tags": ["api"]}]
    r = find_apps_by_tag(apps=apps, tag="webhook")
    assert len(r) == 1

def test_suggest():
    s = suggest_tags(description="Build a webhook integration with OAuth authentication and analytics dashboard")
    assert "webhook" in s
    assert "oauth" in s
    assert "analytics" in s
