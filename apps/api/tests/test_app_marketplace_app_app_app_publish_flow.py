from app.services.app_marketplace_app_app_app_publish_flow import start_publish, run_publish_checks, complete_publish

def test_start():
    r = start_publish(app_id="a1", version="2.0.0", release_notes="Big update")
    assert r["publish_id"].startswith("pub_")
    assert r["status"] == "validating"

def test_checks_pass():
    results = {c: True for c in ["manifest_valid", "tests_passing", "security_scan",
                                   "screenshots", "description", "privacy_policy", "version_bumped"]}
    r = run_publish_checks(results=results)
    assert r["can_publish"]
    assert r["score"] == 100

def test_checks_fail():
    r = run_publish_checks(results={"manifest_valid": True})
    assert not r["can_publish"]
    assert r["passed"] == 1

def test_complete():
    r = complete_publish(publish_id="pub_abc", app_id="a1", version="2.0.0")
    assert r["status"] == "published"
    assert "2.0.0" in r["message"]
