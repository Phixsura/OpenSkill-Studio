from app.services.app_marketplace_app_app_retention_analyzer import analyze_retention

def test_analyze():
    cohorts = [
        {"period": "2026-Q3", "initial_users": 1000,
         "retained_users": [900, 800, 700, 600, 550, 500, 450, 400]},
        {"period": "2026-Q2", "initial_users": 800,
         "retained_users": [720, 640, 560, 480, 440, 400, 360, 320]},
    ]
    r = analyze_retention(cohorts=cohorts)
    assert r["total_cohorts"] == 2
    assert r["cohorts"][0]["day_30"] == 60.0  # 600/1000
    assert r["avg_day_30"] == 60.0  # both are 60%

def test_empty():
    r = analyze_retention(cohorts=[])
    assert r["total_cohorts"] == 0
    assert r["avg_day_30"] is None
