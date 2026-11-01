from app.services.app_marketplace_extension_tagging import TaggingService


def test_create_and_add():
    ts = TaggingService()
    ts.create_tag("Slack", "messaging")
    ts.create_tag("Notifications", "messaging")
    ts.add_tag("ext-1", "slack")
    ts.add_tag("ext-1", "notifications")
    tags = ts.get_extension_tags("ext-1")
    assert len(tags) == 2
    assert any(t.slug == "slack" for t in tags)


def test_usage_count():
    ts = TaggingService()
    ts.create_tag("API")
    ts.add_tag("ext-1", "api")
    ts.add_tag("ext-2", "api")
    assert ts._tags["api"].usage_count == 2


def test_remove_tag():
    ts = TaggingService()
    ts.create_tag("temp")
    ts.add_tag("ext-1", "temp")
    ts.remove_tag("ext-1", "temp")
    assert ts.get_extension_tags("ext-1") == []
    assert ts._tags["temp"].usage_count == 0


def test_extensions_by_tag():
    ts = TaggingService()
    ts.create_tag("tools")
    ts.add_tag("ext-a", "tools")
    ts.add_tag("ext-b", "tools")
    exts = ts.get_extensions_by_tag("tools")
    assert exts == ["ext-a", "ext-b"]


def test_suggest():
    ts = TaggingService()
    ts.create_tag("analytics")
    ts.create_tag("automation")
    ts.create_tag("billing")
    suggestions = ts.suggest("au")
    assert len(suggestions) == 1
    assert suggestions[0].slug == "automation"


def test_popular():
    ts = TaggingService()
    ts.create_tag("popular-tag")
    ts.create_tag("rare-tag")
    for i in range(10):
        ts.add_tag(f"ext-{i}", "popular-tag")
    ts.add_tag("ext-99", "rare-tag")
    popular = ts.get_popular(2)
    assert popular[0].slug == "popular-tag"


def test_related():
    ts = TaggingService()
    ts.create_tag("slack")
    ts.create_tag("messaging")
    ts.create_tag("webhooks")
    ts.add_tag("ext-1", "slack")
    ts.add_tag("ext-1", "messaging")
    ts.add_tag("ext-1", "webhooks")
    related = ts.get_related("slack")
    slugs = [t.slug for t in related]
    assert "messaging" in slugs
    assert "webhooks" in slugs
