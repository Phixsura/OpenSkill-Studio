from app.services.app_marketplace_cookie_consent import get_cookie_config, save_consent, check_consent

def test_config():
    c = get_cookie_config()
    assert "essential" in c["categories"]
    assert c["categories"]["essential"]["required"]

def test_save():
    r = save_consent(user_id="u1", consent={"analytics": True, "marketing": False})
    assert r["consent"]["essential"]
    assert r["consent"]["analytics"]
    assert not r["consent"]["marketing"]

def test_essential_forced():
    r = save_consent(user_id="u1", consent={"essential": False})
    assert r["consent"]["essential"]

def test_check():
    assert check_consent(consent={"analytics": True}, category="analytics")
    assert not check_consent(consent={"analytics": False}, category="marketing")
    assert check_consent(consent={}, category="essential")
