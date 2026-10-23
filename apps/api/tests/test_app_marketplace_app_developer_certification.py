from app.services.app_marketplace_app_developer_certification import take_exam, get_certification_progress

def test_pass():
    r = take_exam(cert_id="platform_basics", score=90)
    assert r["passed"]
    assert r["certificate_id"] is not None

def test_fail():
    r = take_exam(cert_id="security_specialist", score=70)
    assert not r["passed"]
    assert r["certificate_id"] is None

def test_unknown():
    r = take_exam(cert_id="quantum", score=100)
    assert "error" in r

def test_progress():
    r = get_certification_progress(completed=["platform_basics", "api_expert"])
    assert r["completed"] == 2
    assert r["progress_pct"] == 50
