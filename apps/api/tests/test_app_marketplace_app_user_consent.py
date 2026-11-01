from app.services.app_marketplace_app_user_consent import get_consent_options, save_consent

def test_options():
    r = get_consent_options()
    assert r["total"] == 5
    essential = next(c for c in r["categories"] if c["id"] == "essential")
    assert essential["required"]

def test_save():
    r = save_consent(user_id="u1", choices={"analytics": True, "marketing": False, "essential": False})
    assert r["consent"]["essential"]  # forced true
    assert r["consent"]["analytics"]
    assert not r["consent"]["marketing"]
    assert r["optional_accepted"] == 1

def test_save_all():
    choices = {k: True for k in ["analytics", "marketing", "personalization", "third_party"]}
    r = save_consent(user_id="u1", choices=choices)
    assert r["optional_accepted"] == 4
