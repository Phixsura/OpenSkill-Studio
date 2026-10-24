from app.services.app_marketplace_app_app_app_app_app_app_app_cookie_consent import get_consent_options, process_consent

def test_options():
    opts = get_consent_options()
    assert len(opts) == 4
    necessary = next(o for o in opts if o["id"] == "necessary")
    assert necessary["required"]

def test_consent():
    r = process_consent({"analytics": True, "marketing": False})
    assert r["consent"]["necessary"]  # always true
    assert r["consent"]["analytics"]
    assert not r["consent"]["marketing"]
    assert not r["all_accepted"]

def test_accept_all():
    r = process_consent({"analytics": True, "marketing": True, "preferences": True})
    assert r["all_accepted"]
