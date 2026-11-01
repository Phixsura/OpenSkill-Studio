from app.services.app_marketplace_app_changelog_rss import generate_rss_feed

def test_feed():
    entries = [
        {"version": "2.0.0", "title": "Major Update", "description": "New features", "date": "2026-10-23"},
        {"version": "1.1.0", "title": "Bug Fixes", "description": "Stability", "date": "2026-09-15"},
    ]
    r = generate_rss_feed(app_name="MyApp", app_id="app1", entries=entries)
    assert r["item_count"] == 2
    assert r["content_type"] == "application/rss+xml"
    assert "<title>MyApp Changelog</title>" in r["xml"]
    assert "<title>Major Update</title>" in r["xml"]

def test_escaping():
    entries = [{"version": "1.0", "title": "Fix <script>", "description": "A & B", "date": "2026-01-01"}]
    r = generate_rss_feed(app_name="App <XSS>", app_id="a1", entries=entries)
    assert "<script>" not in r["xml"]
    assert "&lt;script&gt;" in r["xml"]
    assert "&amp;" in r["xml"]

def test_empty():
    r = generate_rss_feed(app_name="App", app_id="a1", entries=[])
    assert r["item_count"] == 0
