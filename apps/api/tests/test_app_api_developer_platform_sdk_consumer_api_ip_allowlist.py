"""Tests for Consumer IP Allowlist service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_ip_allowlist import IpAllowlist


class TestIpAllowlist:
    def test_add_and_check_allowed(self):
        svc = IpAllowlist()
        svc.add_entry("c1", "10.0.0.0/24", "office")
        result = svc.check_access("c1", "10.0.0.50")
        assert result["allowed"] is True
        assert result["matched_network"] == "10.0.0.0/24"

    def test_check_not_allowed(self):
        svc = IpAllowlist()
        svc.add_entry("c1", "10.0.0.0/24")
        result = svc.check_access("c1", "192.168.1.1")
        assert result["allowed"] is False

    def test_deny_mode(self):
        svc = IpAllowlist()
        svc.set_mode("c1", "deny")
        svc.add_entry("c1", "10.0.0.0/24", "blocked")
        result = svc.check_access("c1", "10.0.0.5")
        assert result["allowed"] is False
        assert result["reason"] == "ip_denied"
        result2 = svc.check_access("c1", "192.168.1.1")
        assert result2["allowed"] is True

    def test_cidr_single_ip(self):
        svc = IpAllowlist()
        svc.add_entry("c1", "192.168.1.100/32")
        assert svc.check_access("c1", "192.168.1.100")["allowed"] is True
        assert svc.check_access("c1", "192.168.1.101")["allowed"] is False

    def test_remove_entry(self):
        svc = IpAllowlist()
        svc.add_entry("c1", "10.0.0.0/8")
        svc.remove_entry("c1", "10.0.0.0/8")
        assert svc.list_entries("c1") == []

    def test_duplicate_entry(self):
        svc = IpAllowlist()
        svc.add_entry("c1", "10.0.0.0/24")
        with pytest.raises(ValueError):
            svc.add_entry("c1", "10.0.0.0/24")

    def test_invalid_network(self):
        svc = IpAllowlist()
        with pytest.raises(ValueError):
            svc.add_entry("c1", "not-an-ip")

    def test_invalid_mode(self):
        svc = IpAllowlist()
        with pytest.raises(ValueError):
            svc.set_mode("c1", "block")

    def test_stats(self):
        svc = IpAllowlist()
        svc.add_entry("c1", "10.0.0.0/24")
        stats = svc.get_stats("c1")
        assert stats["entry_count"] == 1
        assert stats["total_addresses"] == 256

    def test_no_rules_allows(self):
        svc = IpAllowlist()
        result = svc.check_access("c1", "1.2.3.4")
        assert result["allowed"] is True
        assert result["reason"] == "no_rules"

    def test_isolation(self):
        a, b = IpAllowlist(), IpAllowlist()
        a.add_entry("c1", "10.0.0.0/8")
        assert b.check_access("c1", "10.0.0.1")["reason"] == "no_rules"
