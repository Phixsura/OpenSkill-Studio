"""Tests for App IP Allowlist — add, check, expire."""

import pytest

from app.services.app_ip_allowlist import AppIPAllowlist


class TestAdd:
    def test_add_cidr(self):
        a = AppIPAllowlist()
        e = a.add("inst-1", "e1", "10.0.0.0/24", "Office")
        assert e.cidr == "10.0.0.0/24"

    def test_add_single_ip(self):
        a = AppIPAllowlist()
        e = a.add("inst-1", "e1", "192.168.1.1")
        assert e.is_expired is False

    def test_invalid_cidr(self):
        a = AppIPAllowlist()
        with pytest.raises(ValueError, match="Invalid CIDR"):
            a.add("inst-1", "e1", "not-an-ip")


class TestCheck:
    def test_allowed(self):
        a = AppIPAllowlist()
        a.add("inst-1", "e1", "10.0.0.0/24")
        assert a.is_allowed("inst-1", "10.0.0.5") is True

    def test_denied(self):
        a = AppIPAllowlist()
        a.add("inst-1", "e1", "10.0.0.0/24")
        assert a.is_allowed("inst-1", "192.168.1.1") is False

    def test_empty_denies(self):
        a = AppIPAllowlist()
        assert a.is_allowed("inst-1", "10.0.0.1") is False

    def test_invalid_ip(self):
        a = AppIPAllowlist()
        a.add("inst-1", "e1", "10.0.0.0/24")
        assert a.is_allowed("inst-1", "bad-ip") is False


class TestRemove:
    def test_remove(self):
        a = AppIPAllowlist()
        a.add("inst-1", "e1", "10.0.0.0/24")
        assert a.remove("inst-1", "e1") is True
        assert a.is_allowed("inst-1", "10.0.0.5") is False


class TestIsolation:
    def test_cross(self):
        a = AppIPAllowlist()
        a.add("inst-1", "e1", "10.0.0.0/24")
        assert a.is_allowed("inst-2", "10.0.0.5") is False
