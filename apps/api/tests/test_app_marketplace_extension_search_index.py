from app.services.app_marketplace_extension_search_index import ExtensionSearchIndexService


def test_index_and_search():
    svc = ExtensionSearchIndexService()
    svc.index("ext-1", "Slack Bot", "Send notifications to Slack", "communication", ["slack", "bot"])
    svc.index("ext-2", "GitHub Sync", "Sync issues with GitHub", "integration", ["github"])
    results = svc.search("slack")
    assert len(results) == 1
    assert results[0].name == "Slack Bot"


def test_name_boost():
    svc = ExtensionSearchIndexService()
    svc.index("ext-1", "Slack Connector", "Connect to messaging", "comm")
    svc.index("ext-2", "Email Alerts", "Send slack-like alerts", "comm")
    results = svc.search("slack")
    assert results[0].extension_id == "ext-1"  # name match boosted


def test_category_filter():
    svc = ExtensionSearchIndexService()
    svc.index("ext-1", "Chart Pro", "Charts", "analytics")
    svc.index("ext-2", "Chart Lite", "Charts", "ui")
    results = svc.search("chart", category="analytics")
    assert len(results) == 1


def test_min_rating():
    svc = ExtensionSearchIndexService()
    svc.index("ext-1", "Good Tool", "Useful tool", "tools", rating=4.5)
    svc.index("ext-2", "Bad Tool", "Not great tool", "tools", rating=2.0)
    results = svc.search("tool", min_rating=4.0)
    assert len(results) == 1


def test_autocomplete():
    svc = ExtensionSearchIndexService()
    svc.index("ext-1", "Slack Bot", "desc", "comm")
    svc.index("ext-2", "Slack Alerts", "desc", "comm")
    svc.index("ext-3", "GitHub Sync", "desc", "int")
    suggestions = svc.autocomplete("Slack")
    assert len(suggestions) == 2


def test_facets():
    svc = ExtensionSearchIndexService()
    svc.index("ext-1", "A", "d", "tools", ["api"])
    svc.index("ext-2", "B", "d", "tools", ["api", "data"])
    svc.index("ext-3", "C", "d", "analytics", ["data"])
    facets = svc.get_facets()
    assert facets["categories"]["tools"] == 2
    assert facets["tags"]["api"] == 2
