from app.services.app_marketplace_extension_ip_allowlist import ExtIpAllowlistService

def test_add_and_check():
    svc = ExtIpAllowlistService()
    svc.add("ext-1", "192.168.1.0/24", "Office")
    assert svc.check("ext-1", "192.168.1.50") is True
    assert svc.check("ext-1", "10.0.0.1") is False

def test_no_rules_allow_all():
    svc = ExtIpAllowlistService()
    assert svc.check("ext-1", "1.2.3.4") is True

def test_invalid_cidr():
    svc = ExtIpAllowlistService()
    try:
        svc.add("ext-1", "not-a-cidr")
        assert False
    except ValueError:
        pass

def test_remove():
    svc = ExtIpAllowlistService()
    rule = svc.add("ext-1", "10.0.0.0/8")
    svc.remove("ext-1", rule.rule_id)
    assert svc.check("ext-1", "10.0.0.1") is True  # no rules = allow
