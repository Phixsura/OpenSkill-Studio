from app.services.app_developer_changelog_feed import build_developer_feed, filter_breaking_only

CHANGELOGS = [
    {"app_name": "App A", "entries": [{"version": "2.0", "date": "2026-02", "breaking": True}]},
    {"app_name": "App B", "entries": [{"version": "1.1", "date": "2026-03", "breaking": False}]},
]

def test_merge():
    feed = build_developer_feed(CHANGELOGS)
    assert len(feed) == 2
    assert feed[0]["date"] > feed[1]["date"]

def test_app_name():
    feed = build_developer_feed(CHANGELOGS)
    assert any(e["app_name"] == "App A" for e in feed)

def test_breaking_filter():
    feed = build_developer_feed(CHANGELOGS)
    breaking = filter_breaking_only(feed)
    assert len(breaking) == 1
    assert breaking[0]["app_name"] == "App A"

def test_empty():
    assert build_developer_feed([]) == []
