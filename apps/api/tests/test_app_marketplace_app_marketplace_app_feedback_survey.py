from app.services.app_marketplace_app_marketplace_app_feedback_survey import build_install_survey, build_uninstall_survey, analyze_survey_responses

def test_install():
    s = build_install_survey(app_name="MyApp")
    assert "MyApp" in s["title"]
    assert len(s["questions"]) == 3

def test_uninstall():
    s = build_uninstall_survey(app_name="MyApp")
    assert s["type"] == "post_uninstall"
    assert len(s["questions"]) == 3

def test_analyze():
    responses = [{"rating": 5, "reason": "search"}, {"rating": 4, "reason": "search"}, {"rating": 3, "reason": "social"}]
    r = analyze_survey_responses(responses=responses)
    assert r["total"] == 3
    assert r["avg_rating"] == 4.0
    assert r["top_reasons"][0]["reason"] == "search"
