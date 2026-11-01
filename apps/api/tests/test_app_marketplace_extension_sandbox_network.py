from app.services.app_marketplace_extension_sandbox_network import (
    SandboxNetworkService, RuleAction, Protocol,
)
import pytest


def test_create_policy():
    svc = SandboxNetworkService()
    p = svc.create_policy("ext-1")
    assert p.default_action == RuleAction.DENY
    assert p.bandwidth_limit_kbps == 1024


def test_allow_rule_and_check():
    svc = SandboxNetworkService()
    svc.create_policy("ext-1")
    svc.add_rule("ext-1", RuleAction.ALLOW, "api.example.com", ports=[443])
    r = svc.check_connection("ext-1", "api.example.com", 443, Protocol.HTTPS)
    assert r["allowed"] is True


def test_default_deny():
    svc = SandboxNetworkService()
    svc.create_policy("ext-1")
    r = svc.check_connection("ext-1", "evil.com", 80, Protocol.HTTP)
    assert r["allowed"] is False


def test_block_private_ip():
    svc = SandboxNetworkService()
    svc.create_policy("ext-1", default_action=RuleAction.ALLOW)
    r = svc.check_connection("ext-1", "192.168.1.1", 80, Protocol.HTTP)
    assert r["allowed"] is False
    assert "Private" in r["reason"]


def test_cannot_allow_private_ip_rule():
    svc = SandboxNetworkService()
    svc.create_policy("ext-1")
    with pytest.raises(ValueError, match="private"):
        svc.add_rule("ext-1", RuleAction.ALLOW, "10.0.0.1")


def test_wildcard_pattern():
    svc = SandboxNetworkService()
    svc.create_policy("ext-1")
    svc.add_rule("ext-1", RuleAction.ALLOW, "*.googleapis.com")
    r = svc.check_connection("ext-1", "storage.googleapis.com", 443, Protocol.HTTPS)
    assert r["allowed"] is True


def test_audit_log():
    svc = SandboxNetworkService()
    svc.create_policy("ext-1")
    svc.check_connection("ext-1", "test.com", 80, Protocol.HTTP)
    log = svc.get_audit_log("ext-1")
    assert len(log) == 1
    assert log[0]["host"] == "test.com"


def test_block_cgnat():
    svc = SandboxNetworkService()
    svc.create_policy("ext-1", default_action=RuleAction.ALLOW)
    r = svc.check_connection("ext-1", "100.64.0.1", 80, Protocol.HTTP)
    assert r["allowed"] is False


def test_bare_wildcard_rejected():
    svc = SandboxNetworkService()
    svc.create_policy("ext-1")
    with pytest.raises(ValueError, match="wildcard"):
        svc.add_rule("ext-1", RuleAction.ALLOW, "*")
