from app.services.app_marketplace_changelog_feed import build_changelog_feed, render_rss

def test_feed():
    f = build_changelog_feed(app={"name": "MyApp", "slug": "my-app"},
        versions=[{"version": "2.0", "release_notes": "Big update"}, {"version": "1.0"}])
    assert f["feed_title"] == "MyApp Changelog"
    assert len(f["entries"]) == 2
    assert "Big update" in f["entries"][0]["summary"]

def test_rss():
    f = build_changelog_feed(app={"name": "X", "slug": "x"}, versions=[{"version": "1.0"}])
    xml = render_rss(feed=f)
    assert "<rss" in xml
    assert "X v1.0" in xml

def test_empty():
    f = build_changelog_feed(app={"name": "E", "slug": "e"}, versions=[])
    assert f["updated"] is None
