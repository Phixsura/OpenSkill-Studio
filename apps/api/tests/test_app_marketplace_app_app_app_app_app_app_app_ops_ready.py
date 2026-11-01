from app.services.app_marketplace_app_app_app_app_app_app_app_ops_ready import check_readiness

def test_ready():
    r = check_readiness([
        {"name": "monitoring", "met": True, "severity": "required", "category": "observability"},
        {"name": "runbooks", "met": True, "severity": "required", "category": "ops"},
        {"name": "load_tests", "met": False, "severity": "recommended", "category": "testing"},
    ])
    assert r["ready"]
    assert r["score"] == 67
    assert r["met"] == 2

def test_not_ready():
    r = check_readiness([
        {"name": "monitoring", "met": False, "severity": "required"},
        {"name": "alerts", "met": True, "severity": "required"},
    ])
    assert not r["ready"]
    assert "monitoring" in r["blocking"]
