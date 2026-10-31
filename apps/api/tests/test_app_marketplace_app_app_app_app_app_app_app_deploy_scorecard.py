from app.services.app_marketplace_app_app_app_app_app_app_app_deploy_scorecard import score_deployment

def test_full():
    r = score_deployment({"version": "2.0", "all_tests_passed": True, "security_clean": True,
                           "canary_passed": True, "rollback_tested": True,
                           "monitoring_ready": True, "peer_reviewed": True})
    assert r["score"] == 100
    assert r["grade"] == "A"
    assert r["deploy_ready"]

def test_poor():
    r = score_deployment({"version": "1.5", "all_tests_passed": True})
    assert r["grade"] == "F"
    assert not r["deploy_ready"]
