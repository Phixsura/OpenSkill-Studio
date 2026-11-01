from app.services.app_marketplace_extension_feedback_survey import ExtensionFeedbackSurveyService


def test_create_and_respond():
    svc = ExtensionFeedbackSurveyService()
    qs = svc.create_survey("s1", [
        {"text": "How satisfied?", "type": "rating"},
        {"text": "Any feedback?", "type": "text"},
    ])
    assert len(qs) == 2
    assert svc.submit_response("s1", "user-1", {qs[0].question_id: 5, qs[1].question_id: "Great!"})


def test_no_duplicate():
    svc = ExtensionFeedbackSurveyService()
    qs = svc.create_survey("s1", [{"text": "Rate", "type": "rating"}])
    svc.submit_response("s1", "user-1", {qs[0].question_id: 5})
    assert svc.submit_response("s1", "user-1", {qs[0].question_id: 4}) is False


def test_results():
    svc = ExtensionFeedbackSurveyService()
    qs = svc.create_survey("s1", [{"text": "Rate 1-5", "type": "rating"}])
    qid = qs[0].question_id
    for i, score in enumerate([4, 5, 3, 5, 4]):
        svc.submit_response("s1", f"u_r_{i}", {qid: score})
    results = svc.get_results("s1")
    assert results["responses"] == 5
    assert results["questions"][qid]["average"] == 4.2


def test_nps():
    svc = ExtensionFeedbackSurveyService()
    qs = svc.create_survey("s1", [{"text": "Recommend?", "type": "nps"}])
    qid = qs[0].question_id
    # 3 promoters (9,10,10), 1 passive (7), 1 detractor (3)
    for i, score in enumerate([9, 10, 10, 7, 3]):
        svc.submit_response("s1", f"u{i}", {qid: score})
    nps = svc.calculate_nps("s1", qid)
    assert nps["nps"] == 40.0  # 60% promoters - 20% detractors


def test_choice_question():
    svc = ExtensionFeedbackSurveyService()
    qs = svc.create_survey("s1", [{"text": "Favorite?", "type": "choice", "choices": ["A", "B", "C"]}])
    qid = qs[0].question_id
    for i, choice in enumerate(["A", "B", "A", "C", "A"]):
        svc.submit_response("s1", f"u{i}", {qid: choice})
    results = svc.get_results("s1")
    assert results["questions"][qid]["counts"]["A"] == 3
