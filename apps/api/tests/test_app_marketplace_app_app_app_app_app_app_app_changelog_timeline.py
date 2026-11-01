from app.services.app_marketplace_app_app_app_app_app_app_app_changelog_timeline import build_timeline

def test_timeline():
    r = build_timeline([
        {"version": "3.5.0", "date": "2026-10-24", "title": "SSO & Dark Mode",
         "changes": [{"type": "added"}, {"type": "added"}, {"type": "fixed", "breaking": True}],
         "highlight": True, "tags": ["major"]},
        {"version": "3.4.1", "date": "2026-10-20", "title": "Bug fixes",
         "changes": [{"type": "fixed"}]},
    ])
    assert r["total"] == 2
    assert r["latest"] == "3.5.0"
    assert r["releases"][0]["changes_count"] == 3
    assert r["releases"][0]["breaking_count"] == 1
    assert r["releases"][0]["highlight"]
