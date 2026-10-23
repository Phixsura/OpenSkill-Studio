from app.services.app_marketplace_app_app_changelog_parser import parse_changelog

MD = """# Changelog

## [2.0.0] — 2026-03-01
- Added dark mode support
- Fix login crash on mobile
- New API endpoint for webhooks

## [1.5.0] — 2026-02-01
- Fix memory leak in dashboard
- Added export feature
"""

def test_parse():
    r = parse_changelog(markdown=MD)
    assert r["total_releases"] == 2
    assert r["latest"] == "2.0.0"
    assert r["total_entries"] == 5
    assert r["releases"][0]["entries"][0]["type"] == "feat"
    assert r["releases"][0]["entries"][1]["type"] == "fix"

def test_empty():
    r = parse_changelog(markdown="No releases here")
    assert r["total_releases"] == 0
    assert r["latest"] is None
