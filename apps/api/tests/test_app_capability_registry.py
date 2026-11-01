"""Tests for App Capability Registry — declare, query, version check."""

import pytest

from app.services.app_capability_registry import AppCapabilityRegistry


class TestDeclare:
    def test_declare(self):
        r = AppCapabilityRegistry()
        c = r.declare("inst-1", "webhooks", "Webhooks", "2.0.0")
        assert c.capability_id == "webhooks"
        assert c.version == "2.0.0"

    def test_missing_version(self):
        r = AppCapabilityRegistry()
        with pytest.raises(ValueError, match="version"):
            r.declare("inst-1", "webhooks", "Webhooks", "")

    def test_overwrite(self):
        r = AppCapabilityRegistry()
        r.declare("inst-1", "webhooks", "Webhooks", "1.0.0")
        r.declare("inst-1", "webhooks", "Webhooks v2", "2.0.0")
        c = r.get_capability("inst-1", "webhooks")
        assert c.version == "2.0.0"


class TestQuery:
    def test_has_capability(self):
        r = AppCapabilityRegistry()
        r.declare("inst-1", "webhooks", "Webhooks", "1.0.0")
        assert r.has_capability("inst-1", "webhooks") is True
        assert r.has_capability("inst-1", "nope") is False

    def test_list(self):
        r = AppCapabilityRegistry()
        r.declare("inst-1", "webhooks", "Webhooks", "1.0.0")
        r.declare("inst-1", "oauth", "OAuth", "2.0.0")
        caps = r.list_capabilities("inst-1")
        assert len(caps) == 2

    def test_find_installations(self):
        r = AppCapabilityRegistry()
        r.declare("inst-1", "webhooks", "Webhooks", "1.0.0")
        r.declare("inst-2", "webhooks", "Webhooks", "1.0.0")
        r.declare("inst-3", "oauth", "OAuth", "1.0.0")
        insts = r.find_installations_with("webhooks")
        assert insts == ["inst-1", "inst-2"]


class TestVersionCheck:
    def test_meets_min(self):
        r = AppCapabilityRegistry()
        r.declare("inst-1", "webhooks", "Webhooks", "2.1.0")
        assert r.check_version("inst-1", "webhooks", "2.0.0") is True

    def test_exact_match(self):
        r = AppCapabilityRegistry()
        r.declare("inst-1", "webhooks", "Webhooks", "2.0.0")
        assert r.check_version("inst-1", "webhooks", "2.0.0") is True

    def test_below_min(self):
        r = AppCapabilityRegistry()
        r.declare("inst-1", "webhooks", "Webhooks", "1.5.0")
        assert r.check_version("inst-1", "webhooks", "2.0.0") is False

    def test_missing_capability(self):
        r = AppCapabilityRegistry()
        assert r.check_version("inst-1", "nope", "1.0.0") is False


class TestRevoke:
    def test_revoke(self):
        r = AppCapabilityRegistry()
        r.declare("inst-1", "webhooks", "Webhooks", "1.0.0")
        assert r.revoke("inst-1", "webhooks") is True
        assert r.has_capability("inst-1", "webhooks") is False

    def test_revoke_nonexistent(self):
        r = AppCapabilityRegistry()
        assert r.revoke("inst-1", "nope") is False


class TestIsolation:
    def test_cross_installation(self):
        r = AppCapabilityRegistry()
        r.declare("inst-1", "webhooks", "Webhooks", "1.0.0")
        assert r.has_capability("inst-2", "webhooks") is False
