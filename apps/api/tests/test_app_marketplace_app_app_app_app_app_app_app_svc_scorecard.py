from app.services.app_marketplace_app_app_app_app_app_app_app_svc_scorecard import score_service

def test_score():
    r = score_service("api", {"reliability": 95, "performance": 88,
                                 "security": 92, "observability": 85, "documentation": 70})
    assert r["overall_grade"] in ("A", "B")
    assert r["avg_score"] == 86
    assert len(r["dimensions"]) == 5
