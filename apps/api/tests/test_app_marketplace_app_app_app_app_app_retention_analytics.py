from app.services.app_marketplace_app_app_app_app_app_retention_analytics import build_retention_cohorts

def test_cohorts():
    cohorts = [
        {"cohort": "2026-W40", "size": 100, "weekly_retention": [80, 60, 50, 45]},
        {"cohort": "2026-W41", "size": 120, "weekly_retention": [90, 70, 55, 50]},
    ]
    r = build_retention_cohorts(cohorts=cohorts)
    assert r["total_cohorts"] == 2
    assert r["avg_week1_retention"] == 85.0
    assert r["avg_week4_retention"] == 47.5
