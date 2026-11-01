from app.services.app_marketplace_app_app_changelog_rss import build_rss_feed, build_atom_feed

ENTRIES = [
    {"title": "v2.0.0 Released", "version": "2.0.0", "description": "Major update", "date": "2026-03-01"},
    {"title": "v1.5.0 Released", "version": "1.5.0", "description": "Minor update", "date": "2026-02-01"},
]

def test_rss():
    r = build_rss_feed(app_name="SuperApp", base_url="https://marketplace.openskill.dev", entries=ENTRIES)
    assert r["entry_count"] == 2
    assert "<rss" in r["xml"]
    assert "SuperApp" in r["xml"]

def test_atom():
    r = build_atom_feed(app_name="SuperApp", base_url="https://marketplace.openskill.dev", entries=ENTRIES)
    assert "<feed" in r["xml"]
    assert r["content_type"] == "application/atom+xml"
