from app.services.app_marketplace_app_user_feedback_survey import create_survey, calculate_nps

def test_create_nps():
    r = create_survey(app_id="a1", survey_type="nps")
    assert r["survey_id"].startswith("srv_")
    assert r["questions"][0]["max"] == 10

def test_create_invalid():
    r = create_survey(app_id="a1", survey_type="bad")
    assert "error" in r

def test_nps_excellent():
    # 8 promoters (9-10), 1 passive (7-8), 1 detractor (0-6)
    responses = [10, 9, 10, 9, 10, 9, 10, 9, 7, 5]
    r = calculate_nps(responses=responses)
    assert r["nps_score"] == 70.0
    assert r["category"] == "excellent"

def test_nps_negative():
    responses = [3, 4, 5, 6, 2]
    r = calculate_nps(responses=responses)
    assert r["nps_score"] < 0
    assert r["category"] == "needs_improvement"
