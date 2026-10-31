from app.services.app_marketplace_app_app_app_app_app_app_app_team_perf import track_team_performance

def test_excellent():
    r = track_team_performance("platform", {
        "story_points": 60, "avg_cycle_time_days": 3,
        "deploys_per_week": 8, "incidents_caused": 0, "avg_pr_review_hours": 4})
    assert r["rating"] == "excellent"
    assert r["health_score"] >= 80

def test_needs_improvement():
    r = track_team_performance("legacy", {
        "story_points": 10, "avg_cycle_time_days": 14,
        "deploys_per_week": 0, "incidents_caused": 5, "avg_pr_review_hours": 48})
    assert r["rating"] == "needs_improvement"
