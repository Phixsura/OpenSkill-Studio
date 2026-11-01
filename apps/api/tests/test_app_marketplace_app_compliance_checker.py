from app.services.app_marketplace_app_compliance_checker import check_compliance

def test_gdpr_compliant():
    features = {"gdpr_privacy": True, "gdpr_data_export": True, "gdpr_data_delete": True, "gdpr_consent": True}
    r = check_compliance(framework="gdpr", app_features=features)
    assert r["compliant"]
    assert r["score"] == 100

def test_gdpr_non_compliant():
    r = check_compliance(framework="gdpr", app_features={"gdpr_privacy": True})
    assert not r["compliant"]
    assert r["passed"] == 1

def test_a11y():
    features = {"a11y_alt_text": True, "a11y_keyboard": True}
    r = check_compliance(framework="accessibility", app_features=features)
    assert r["compliant"]  # required met, optional contrast missing is just warning

def test_unknown():
    r = check_compliance(framework="hipaa", app_features={})
    assert "error" in r
