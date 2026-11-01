from app.services.app_marketplace_extension_dns_resolver import DNSResolverService


def test_register_subdomain():
    dns = DNSResolverService()
    mapping, msg = dns.register_subdomain("myext", "ext-1", "org-1")
    assert mapping is not None
    assert mapping.domain == "myext.ext.openskill.dev"
    assert mapping.status == "active"


def test_reserved_subdomain():
    dns = DNSResolverService()
    mapping, msg = dns.register_subdomain("api", "ext-1", "org-1")
    assert mapping is None
    assert "reserved" in msg


def test_duplicate_subdomain():
    dns = DNSResolverService()
    dns.register_subdomain("taken", "ext-1", "org-1")
    mapping, msg = dns.register_subdomain("taken", "ext-2", "org-2")
    assert mapping is None
    assert "already registered" in msg


def test_custom_domain_flow():
    dns = DNSResolverService()
    mapping, msg = dns.register_custom_domain("slack.mycompany.com", "ext-1", "org-1")
    assert mapping.status == "pending"
    assert "osk-verify-" in msg

    # Verify with correct token
    ok, _ = dns.verify_domain("slack.mycompany.com", mapping.verification_token)
    assert ok is True
    assert dns._mappings["slack.mycompany.com"].status == "verified"

    # Activate
    assert dns.activate("slack.mycompany.com") is True
    resolved = dns.resolve("slack.mycompany.com")
    assert resolved is not None


def test_wrong_token():
    dns = DNSResolverService()
    dns.register_custom_domain("bad.com", "ext-2", "org-2")
    ok, msg = dns.verify_domain("bad.com", "wrong-token")
    assert ok is False
    assert "mismatch" in msg


def test_list_and_remove():
    dns = DNSResolverService()
    dns.register_subdomain("a", "ext-3", "org-1")
    dns.register_subdomain("b", "ext-3", "org-1")
    assert len(dns.list_domains("ext-3")) == 2
    dns.remove_domain("a.ext.openskill.dev")
    assert len(dns.list_domains("ext-3")) == 1
