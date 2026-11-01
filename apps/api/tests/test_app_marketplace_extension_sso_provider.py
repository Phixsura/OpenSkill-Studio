from app.services.app_marketplace_extension_sso_provider import ExtSSOProviderService

def test_create_and_validate():
    svc = ExtSSOProviderService()
    svc.trust_extension("ext-1")
    session = svc.create_session("u1", "ext-1")
    result = svc.validate(session.token)
    assert result is not None
    assert result.user_id == "u1"

def test_untrusted():
    svc = ExtSSOProviderService()
    try:
        svc.create_session("u1", "ext-unknown")
        assert False
    except ValueError:
        pass

def test_revoke():
    svc = ExtSSOProviderService()
    svc.trust_extension("ext-1")
    s = svc.create_session("u1", "ext-1")
    svc.revoke(s.session_id)
    assert svc.validate(s.token) is None

def test_invalid_token():
    svc = ExtSSOProviderService()
    assert svc.validate("bad-token") is None
