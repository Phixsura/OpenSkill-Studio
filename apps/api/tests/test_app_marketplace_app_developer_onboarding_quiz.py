from app.services.app_marketplace_app_developer_onboarding_quiz import get_quiz, evaluate_quiz

def test_quiz():
    q = get_quiz()
    assert len(q) == 4

def test_expert():
    r = evaluate_quiz(answers={"q1": "Expert", "q2": "Regularly", "q3": "Python", "q4": "Publish to marketplace"})
    assert r["level"] == "expert"
    assert r["skip_basics"]

def test_beginner():
    r = evaluate_quiz(answers={"q1": "Beginner", "q2": "No"})
    assert r["level"] == "beginner"
    assert not r["skip_basics"]

def test_intermediate():
    r = evaluate_quiz(answers={"q1": "Intermediate", "q2": "A few times"})
    assert r["level"] == "intermediate"
