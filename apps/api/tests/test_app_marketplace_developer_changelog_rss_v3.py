from app.services.app_marketplace_developer_changelog_rss_v3 import build_platform_rss, render_rss_xml

def test_rss():
    r = build_platform_rss(
        app_updates=[{"app_name": "App1", "version": "2.0", "slug": "app1", "released_at": "2026-10-01"}],
        platform_updates=[{"title": "API v3 Released", "date": "2026-10-15"}])
    assert r["entry_count"] == 2
    assert r["entries"][0]["date"] == "2026-10-15"

def test_xml():
    feed = {"title": "Updates", "link": "https://x.com/feed", "entries": [
        {"title": "App v2", "link": "https://x.com/app", "date": "2026-10-01"}]}
    xml = render_rss_xml(feed=feed)
    assert "<rss" in xml
    assert "App v2" in xml
