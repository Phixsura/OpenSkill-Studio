from app.services.app_marketplace_app_app_app_app_app_app_app_app_changelog_view import format_changelog

def test_changelog():
    r = format_changelog([
        {"version": "2.0.0", "date": "2026-10-24", "summary": "Major release",
         "changes": [{"type": "added", "text": "SSO support"},
                     {"type": "fixed", "text": "Login bug"}]},
        {"version": "1.5.0", "date": "2026-10-01",
         "changes": [{"type": "performance", "text": "Faster queries"}]},
    ])
    assert r["total_versions"] == 2
    assert r["total_changes"] == 3
    assert r["versions"][0]["changes"][0]["icon"] == "✨"
    assert r["versions"][0]["change_count"] == 2
