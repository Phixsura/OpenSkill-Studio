"""Tests for App IP Allow List — rules, matching, CIDR, modes."""

import pytest

from app.services.app_ip_allowlist import AppIPAllowList


class TestAddRule:
    def test_add_ip(self):
        l = AppIPAllowList()
        r = l.add_rule("inst-1", "r1", "10.0.0.1")
        assert r.network == "10.0.0.1/32"

    def test_add_cidr(self):
        l = AppIPAllowList()
        r = l.add_rule("inst-1", "r1", "192.168.1.0/24")
        assert r.network == "192.168.1.0/24"

    def test_invalid_network(self):
        l = AppIPAllowList()
        with pytest.raises(ValueError, match="Invalid network"):
            l.add_rule("inst-1", "r1", "not-an-ip")

    def test_duplicate_rule_id(self):
        l = AppIPAllowList()
        l.add_rule("inst-1", "r1", "10.0.0.1")
        with pytest.raises(ValueError, match="already exists"):
            l.add_rule("inst-1", "r1", "10.0.0.2")


class TestRemoveRule:
    def test_remove(self):
        l = AppIPAllowList()
        l.add_rule("inst-1", "r1", "10.0.0.1")
        assert l.remove_rule("inst-1", "r1") is True
        assert len(l.list_rules("inst-1")) == 0

    def test_remove_nonexistent(self):
        l = AppIPAllowList()
        assert l.remove_rule("inst-1", "nope") is False


class TestAllowlistMode:
    def test_no_rules_allows_all(self):
        l = AppIPAllowList(mode="allowlist")
        assert l.check_ip("inst-1", "1.2.3.4") is True

    def test_exact_ip_match(self):
        l = AppIPAllowList(mode="allowlist")
        l.add_rule("inst-1", "r1", "10.0.0.1")
        assert l.check_ip("inst-1", "10.0.0.1") is True
        assert l.check_ip("inst-1", "10.0.0.2") is False

    def test_cidr_match(self):
        l = AppIPAllowList(mode="allowlist")
        l.add_rule("inst-1", "r1", "192.168.1.0/24")
        assert l.check_ip("inst-1", "192.168.1.50") is True
        assert l.check_ip("inst-1", "192.168.2.1") is False


class TestDenylistMode:
    def test_no_rules_allows_all(self):
        l = AppIPAllowList(mode="denylist")
        assert l.check_ip("inst-1", "1.2.3.4") is True

    def test_denied_ip(self):
        l = AppIPAllowList(mode="denylist")
        l.add_rule("inst-1", "r1", "10.0.0.1")
        assert l.check_ip("inst-1", "10.0.0.1") is False
        assert l.check_ip("inst-1", "10.0.0.2") is True

    def test_denied_cidr(self):
        l = AppIPAllowList(mode="denylist")
        l.add_rule("inst-1", "r1", "172.16.0.0/16")
        assert l.check_ip("inst-1", "172.16.5.10") is False
        assert l.check_ip("inst-1", "172.17.0.1") is True


class TestInvalidIP:
    def test_invalid_returns_false(self):
        l = AppIPAllowList()
        assert l.check_ip("inst-1", "not-an-ip") is False


class TestIsolation:
    def test_cross_installation(self):
        l = AppIPAllowList(mode="allowlist")
        l.add_rule("inst-1", "r1", "10.0.0.1")
        # inst-2 has no rules → allow all
        assert l.check_ip("inst-2", "10.0.0.1") is True


class TestConfig:
    def test_invalid_mode(self):
        with pytest.raises(ValueError, match="mode"):
            AppIPAllowList(mode="block")
