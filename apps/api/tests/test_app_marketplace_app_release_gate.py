from app.services.app_marketplace_app_release_gate import evaluate_gates

def test_all_pass():
    results = {g: True for g in ["tests", "security_scan", "performance", "code_review", "staging_deploy", "smoke_test", "changelog"]}
    r = evaluate_gates(results=results)
    assert r["release_ready"]
    assert r["passed"] == 7
    assert len(r["blocking"]) == 0

def test_blocking():
    results = {"tests": True, "security_scan": False, "code_review": True, "staging_deploy": True, "smoke_test": True}
    r = evaluate_gates(results=results)
    assert not r["release_ready"]
    assert "security_scan" in r["blocking"]

def test_optional_skip():
    results = {"tests": True, "security_scan": True, "code_review": True, "staging_deploy": True, "smoke_test": True}
    r = evaluate_gates(results=results)
    assert r["release_ready"]  # optional gates not blocking
