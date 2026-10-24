from app.services.app_marketplace_app_app_app_app_app_app_app_scorecard import calculate_scorecard

def test_scorecard():
    r = calculate_scorecard({
        "reliability": 99.95, "performance": 92, "security": 100,
        "developer_experience": 88, "cost_efficiency": 90,
    })
    assert r["total_score"] > 90
    assert r["grade"] in ("A+", "A")
    assert r["targets_met"] >= 3

def test_low():
    r = calculate_scorecard({"reliability": 50, "performance": 40})
    assert r["grade"] in ("C", "D")
