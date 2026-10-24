from app.services.app_marketplace_app_app_team_activity import build_team_activity

def test_activity():
    activities = [
        {"actor": "Alice", "action": "deployed", "target": "v2.0.0", "timestamp": "2026-01-03"},
        {"actor": "Bob", "action": "reviewed", "target": "PR #42", "timestamp": "2026-01-02"},
        {"actor": "Alice", "action": "committed", "target": "feat: dark mode", "timestamp": "2026-01-01"},
    ]
    r = build_team_activity(activities=activities)
    assert r["total"] == 3
    assert r["unique_members"] == 2
    assert r["top_contributors"][0]["name"] == "Alice"
    assert r["top_contributors"][0]["count"] == 2
