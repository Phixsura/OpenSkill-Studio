from app.services.app_marketplace_app_app_app_app_app_app_app_certification import evaluate_exam, list_certifications

def test_pass():
    r = evaluate_exam("platform_basics", score=90, modules_completed=5)
    assert r["passed"]
    assert r["badge"] is not None

def test_fail():
    r = evaluate_exam("api_expert", score=70, modules_completed=8)
    assert not r["passed"]
    assert r["badge"] is None

def test_list():
    assert len(list_certifications()) == 4
