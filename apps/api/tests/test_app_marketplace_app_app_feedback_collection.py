from app.services.app_marketplace_app_app_feedback_collection import build_survey, submit_survey

def test_survey():
    questions = [
        {"text": "How would you rate this app?", "type": "rating", "required": True},
        {"text": "What could be improved?", "type": "text"},
        {"text": "Would you recommend?", "type": "nps"},
    ]
    r = build_survey(title="App Feedback", questions=questions)
    assert r["question_count"] == 3
    assert r["title"] == "App Feedback"
    assert r["estimated_time_min"] == 1

def test_submit():
    r = submit_survey(survey_id="s1", answers={"q1": 5, "q2": "Great!"})
    assert r["submission_id"].startswith("sub_")
    assert r["answer_count"] == 2
