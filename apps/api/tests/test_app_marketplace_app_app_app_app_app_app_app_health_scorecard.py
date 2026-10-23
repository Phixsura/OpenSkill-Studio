from app.services.app_marketplace_app_app_app_app_app_app_app_health_scorecard import compute_scorecard

def test_scorecard():
    dims = [
        {"name": "Uptime", "score": 99, "weight": 3},
        {"name": "Performance", "score": 85, "weight": 2},
        {"name": "Security", "score": 92, "weight": 3},
        {"name": "Reliability", "score": 45, "weight": 2, "details": "High error rate"},
    ]
    r = compute_scorecard(dims)
    assert r["overall_score"] > 0
    assert r["dimension_count"] == 4
    assert "Reliability" in r["poor_dimensions"]
    assert r["needs_attention"]
    assert r["dimensions"][0]["status"] == "excellent"
