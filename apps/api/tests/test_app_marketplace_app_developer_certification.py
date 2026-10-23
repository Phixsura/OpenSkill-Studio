from app.services.app_marketplace_app_developer_certification import check_certification, get_developer_badges, list_available_certifications

def test_earned():
    r = check_certification(cert_id="marketplace_basics", completed_tasks=5)
    assert r["earned"]
    assert r["pct"] == 100

def test_not_earned():
    r = check_certification(cert_id="security_expert", completed_tasks=2)
    assert not r["earned"]
    assert r["pct"] == 40

def test_unknown():
    r = check_certification(cert_id="nonexistent", completed_tasks=10)
    assert r["error"]

def test_badges():
    b = get_developer_badges(completed_certs=["marketplace_basics", "security_expert"])
    assert len(b) == 2

def test_list():
    c = list_available_certifications()
    assert len(c) == 4
