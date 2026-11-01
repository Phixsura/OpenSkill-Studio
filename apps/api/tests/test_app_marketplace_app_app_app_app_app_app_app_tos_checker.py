from app.services.app_marketplace_app_app_app_app_app_app_app_tos_checker import check_compliance

def test_compliant():
    r = check_compliance({"data_privacy": True, "no_malware": True, "rate_limits": True,
                            "branding": True, "support": True})
    assert r["compliant"]
    assert r["score"] == 100

def test_non_compliant():
    r = check_compliance({"data_privacy": True, "no_malware": False, "rate_limits": True})
    assert not r["compliant"]
    assert r["score"] < 100
    critical = [x for x in r["results"] if x["critical"]]
    assert len(critical) >= 1
