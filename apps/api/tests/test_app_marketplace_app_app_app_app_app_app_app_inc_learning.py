from app.services.app_marketplace_app_app_app_app_app_app_app_inc_learning import extract_learnings, learning_trends

def test_learnings():
    r = extract_learnings({"id": "INC-1", "detection_time_min": 60,
                              "resolution_time_min": 180, "had_runbook": False,
                              "affected_customers": 500})
    assert r["lesson_count"] == 4
    assert any(l["area"] == "detection" for l in r["lessons"])

def test_trends():
    reviews = [
        {"lessons": [{"area": "detection"}, {"area": "response"}]},
        {"lessons": [{"area": "detection"}]},
    ]
    r = learning_trends(reviews)
    assert r["top_area"] == "detection"
    assert r["total_lessons"] == 3
