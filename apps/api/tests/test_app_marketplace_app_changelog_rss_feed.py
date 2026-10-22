from app.services.app_marketplace_app_changelog_rss_feed import build_global_feed, build_atom_xml

def test_feed():
    updates = [{"app_name": "App1", "app_slug": "app1", "version": "2.0",
                "released_at": "2026-06-01T00:00:00Z", "developer_name": "Dev", "release_notes": "Big update"}]
    f = build_global_feed(updates=updates)
    assert f["entry_count"] == 1
    assert "App1 v2.0" in f["entries"][0]["title"]

def test_atom():
    feed = {"feed_title": "Updates", "feed_link": "https://x.com/feed", "updated": "2026-01-01",
            "entries": [{"title": "App v1", "link": "https://x.com/app", "published": "2026-01-01", "summary": "New"}]}
    xml = build_atom_xml(feed=feed)
    assert "<feed" in xml
    assert "App v1" in xml
