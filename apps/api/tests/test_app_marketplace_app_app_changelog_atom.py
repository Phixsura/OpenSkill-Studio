from app.services.app_marketplace_app_app_changelog_atom import generate_atom_feed

def test_feed():
    entries = [
        {"version": "2.0", "title": "Major Update", "summary": "New features", "date": "2026-10-23"},
        {"version": "1.1", "title": "Bug Fix", "summary": "Fixes", "date": "2026-09-15"},
    ]
    r = generate_atom_feed(app_name="Auth SDK", app_id="auth", entries=entries)
    assert r["entry_count"] == 2
    assert r["content_type"] == "application/atom+xml"
    assert "<title>Auth SDK Changelog</title>" in r["xml"]
    assert "<title>Major Update</title>" in r["xml"]

def test_escaping():
    entries = [{"version": "1.0", "title": "<script>", "summary": "A & B", "date": "2026-01-01"}]
    r = generate_atom_feed(app_name="App <XSS>", app_id="a1", entries=entries)
    assert "<script>" not in r["xml"]
    assert "&amp;" in r["xml"]
