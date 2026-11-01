from app.services.app_marketplace_app_app_consent_manager import build_consent_form, record_consent

def test_form_defaults():
    r = build_consent_form()
    assert r["total"] == 4
    essential = next(i for i in r["items"] if i["type"] == "essential")
    assert essential["granted"]
    assert essential["required"]
    analytics = next(i for i in r["items"] if i["type"] == "analytics")
    assert not analytics["granted"]

def test_record():
    r = record_consent(user_id="u1", consents={"analytics": True, "marketing": False})
    assert r["consents"]["essential"]  # forced true
    assert r["consents"]["analytics"]
    assert not r["consents"]["marketing"]
    assert r["id"].startswith("consent_")
