from app.services.app_marketplace_app_app_app_app_app_app_app_rss_feed import build_rss_feed, filter_feed

def test_rss():
    feed = build_rss_feed(
        title="OpenSkill Updates", link="https://openskill.io/feed",
        entries=[
            {"title": "v3.2 Released", "link": "/blog/v32", "date": "2026-10-24", "category": "release"},
            {"title": "New SDK", "link": "/blog/sdk", "date": "2026-10-23", "category": "announcement"},
            {"title": "Bug Fix", "link": "/blog/fix", "date": "2026-10-22", "category": "release"},
        ])
    assert feed["item_count"] == 3
    assert "OpenSkill" in feed["xml_preview"]

def test_filter():
    feed = build_rss_feed(title="Test", link="/", entries=[
        {"title": "A", "category": "release"}, {"title": "B", "category": "blog"},
    ])
    f = filter_feed(feed, category="release")
    assert f["item_count"] == 1
    assert f["filtered"]
