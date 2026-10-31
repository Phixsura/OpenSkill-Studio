from app.services.app_marketplace_app_app_app_app_app_app_app_security_scan import run_security_scan, check_url_security

def test_scan_pass():
    r = run_security_scan({"check_https_only": True, "check_no_secrets": True,
                            "check_csp_headers": True, "check_input_validation": True,
                            "check_rate_limiting": True})
    assert r["status"] == "passed"
    assert r["score"] == 100

def test_scan_fail():
    r = run_security_scan({"check_no_secrets": False})
    assert r["status"] == "failed"
    assert r["critical_failures"] == 1

def test_url():
    assert check_url_security("https://api.example.com")["secure"]
    assert not check_url_security("http://insecure.com")["secure"]
