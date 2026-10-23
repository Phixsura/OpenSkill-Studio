from app.services.app_marketplace_app_developer_activity_summary import build_weekly_summary

def test_summary():
    activity = {"commits": 15, "deploys": 3, "reviews_received": 8,
                "new_installs": 200, "revenue": 500.50, "streak_days": 5}
    r = build_weekly_summary(developer_name="Alice", week="2026-W43", activity=activity)
    assert r["developer_name"] == "Alice"
    assert r["activity"]["commits"] == 15
    assert r["activity"]["revenue"] == 500.50
    assert r["top_achievement"] == "📈 Growth Milestone"

def test_streak():
    r = build_weekly_summary(developer_name="Bob", week="W1",
        activity={"streak_days": 10, "commits": 5})
    assert r["top_achievement"] == "🔥 7-Day Streak"
