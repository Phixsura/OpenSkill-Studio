from app.services.app_marketplace_app_app_app_changelog_viewer import build_changelog_viewer

def test_viewer():
    releases = [
        {"version": "2.0.0", "date": "2026-03-01", "entries": [
            {"type": "added", "text": "Dark mode"}, {"type": "breaking", "text": "Removed v1 API"}]},
        {"version": "1.5.0", "date": "2026-02-01", "entries": [{"type": "fixed", "text": "Login bug"}]},
    ]
    r = build_changelog_viewer(app_name="SuperApp", releases=releases)
    assert r["total_releases"] == 2
    assert r["total_changes"] == 3
    assert r["latest"] == "2.0.0"
    assert r["releases"][0]["has_breaking"]
