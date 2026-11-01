from app.services.app_marketplace_app_app_changelog import build_changelog

def test_changelog():
    releases = [
        {"version": "2.0.0", "date": "2026-01-15", "entries": [
            {"type": "breaking", "message": "Removed legacy API"},
            {"type": "feat", "message": "New dashboard"},
        ]},
        {"version": "1.5.0", "date": "2026-01-01", "entries": [
            {"type": "fix", "message": "Fixed login bug"},
        ]},
    ]
    r = build_changelog(releases=releases)
    assert r["total_releases"] == 2
    assert r["latest"] == "2.0.0"
    assert r["releases"][0]["has_breaking"]
    assert not r["releases"][1]["has_breaking"]
    assert r["releases"][0]["entries"][0]["icon"] == "💥"

def test_empty():
    r = build_changelog(releases=[])
    assert r["latest"] is None
