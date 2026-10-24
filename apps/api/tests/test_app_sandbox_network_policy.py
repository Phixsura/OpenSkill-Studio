from app.services.app_sandbox_network_policy import build_network_rules, check_host_allowed, validate_network_config

def test_deny_all():
    r = build_network_rules(egress_policy="deny", allowed_hosts=[])
    assert r["allow_network"] is False

def test_allowlist():
    r = build_network_rules(egress_policy="allowlist", allowed_hosts=["api.example.com", "hooks.slack.com"])
    assert r["allow_network"] is True
    assert "api.example.com" in r["allowed_hosts"]

def test_check_allowed():
    r = build_network_rules(egress_policy="allowlist", allowed_hosts=["api.example.com"])
    assert check_host_allowed("api.example.com", r) is True
    assert check_host_allowed("evil.com", r) is False

def test_check_deny():
    r = build_network_rules(egress_policy="deny", allowed_hosts=[])
    assert check_host_allowed("anything.com", r) is False

def test_validate_ok():
    assert validate_network_config({"egress_policy": "allowlist", "allowed_hosts": ["x.com"]}) == []

def test_validate_bad_policy():
    assert len(validate_network_config({"egress_policy": "yolo"})) > 0

def test_validate_deny_with_hosts():
    assert len(validate_network_config({"egress_policy": "deny", "allowed_hosts": ["x.com"]})) > 0
