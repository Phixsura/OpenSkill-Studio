from app.services.app_marketplace_extension_custom_domain import ExtCustomDomainService

def test_add_and_verify():
    svc = ExtCustomDomainService()
    cd = svc.add("ext-1", "docs.myext.com")
    assert cd.verified is False
    assert svc.verify("docs.myext.com", cd.verification_token) is True
    assert cd.ssl_active is True

def test_invalid_domain():
    svc = ExtCustomDomainService()
    try:
        svc.add("ext-1", "not a domain!")
        assert False
    except ValueError:
        pass

def test_resolve():
    svc = ExtCustomDomainService()
    cd = svc.add("ext-1", "app.example.com")
    assert svc.resolve("app.example.com") is None  # not verified
    svc.verify("app.example.com", cd.verification_token)
    assert svc.resolve("app.example.com") == "ext-1"

def test_remove():
    svc = ExtCustomDomainService()
    svc.add("ext-1", "test.example.com")
    assert svc.remove("test.example.com", "ext-1") is True
    assert svc.remove("test.example.com", "ext-1") is False
