from app.services.app_marketplace_app_app_cookie_consent import build_cookie_policy, save_consent

def test_policy():
    r = build_cookie_policy(domain="marketplace.openskill.dev")
    assert r["total"] == 4
    necessary = next(c for c in r["categories"] if c["id"] == "necessary")
    assert necessary["consented"]
    assert necessary["required"]

def test_save():
    r = save_consent(user_id="u1", consents={"analytics": True, "advertising": False})
    assert r["consents"]["necessary"]  # forced
    assert r["consents"]["analytics"]
    assert not r["consents"]["advertising"]
    assert r["consent_id"].startswith("cc_")
