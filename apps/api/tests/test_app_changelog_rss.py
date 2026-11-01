from app.services.app_changelog_rss import build_rss_feed

def test_basic_feed():
    rss = build_rss_feed(app_name="Test App", app_slug="test-app", entries=[
        {"version": "2.0.0", "notes": "Big update", "date": "2026-01-01"},
        {"version": "1.0.0", "notes": "Initial", "date": "2025-06-01"},
    ])
    assert '<?xml' in rss
    assert '<rss' in rss
    assert 'Test App' in rss
    assert 'v2.0.0' in rss

def test_empty():
    rss = build_rss_feed(app_name="X", app_slug="x", entries=[])
    assert '<channel>' in rss

def test_link():
    rss = build_rss_feed(app_name="X", app_slug="my-app", entries=[{"version": "1.0"}])
    assert 'my-app' in rss
