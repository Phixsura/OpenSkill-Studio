from app.services.app_marketplace_app_developer_survey import create_survey, submit_response, compute_survey_results

def test_create():
    s = create_survey(title="Feedback", questions=[{"type": "rating", "text": "How satisfied?"}])
    assert s["status"] == "draft"

def test_invalid_type():
    s = create_survey(title="X", questions=[{"type": "slider", "text": "Q"}])
    assert s["error"]

def test_submit():
    r = submit_response(survey_id="s1", answers=[{"value": 5}])
    assert r["survey_id"] == "s1"

def test_results():
    questions = [{"type": "rating", "text": "Satisfaction"}]
    responses = [{"answers": [{"value": 5}]}, {"answers": [{"value": 3}]}]
    r = compute_survey_results(responses=responses, questions=questions)
    assert r["results"][0]["average"] == 4.0
    assert r["total_responses"] == 2
