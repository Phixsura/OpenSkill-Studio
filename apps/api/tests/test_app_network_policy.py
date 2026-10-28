"""Tests for App Network Policy — rules, egress checks."""

import pytest

from app.services.app_network_policy import AppNetworkPolicy, NetworkRule


class TestAddRule:
    def test_add(self):
        p = AppNetworkPolicy()
        r = p.add_rule("inst-1", NetworkRule(rule_id="r1", direction="egress", action="allow", destination="api.stripe.com"))
        assert r.destination == "api.stripe.com"

    def test_invalid_direction(self):
        p = AppNetworkPolicy()
        with pytest.raises(ValueError, match="direction"):
            p.add_rule("inst-1", NetworkRule(rule_id="r1", direction="both", action="allow", destination="*"))

    def test_invalid_action(self):
        p = AppNetworkPolicy()
        with pytest.raises(ValueError, match="action"):
            p.add_rule("inst-1", NetworkRule(rule_id="r1", direction="egress", action="block", destination="*"))

    def test_duplicate(self):
        p = AppNetworkPolicy()
        p.add_rule("inst-1", NetworkRule(rule_id="r1", direction="egress", action="allow", destination="*"))
        with pytest.raises(ValueError):
            p.add_rule("inst-1", NetworkRule(rule_id="r1", direction="egress", action="deny", destination="*"))


class TestEgressCheck:
    def test_no_rules_allows(self):
        p = AppNetworkPolicy()
        assert p.check_egress("inst-1", "any.com") is True

    def test_allow_rule(self):
        p = AppNetworkPolicy()
        p.add_rule("inst-1", NetworkRule(rule_id="r1", direction="egress", action="allow", destination="api.stripe.com"))
        assert p.check_egress("inst-1", "api.stripe.com") is True

    def test_deny_rule(self):
        p = AppNetworkPolicy()
        p.add_rule("inst-1", NetworkRule(rule_id="r1", direction="egress", action="deny", destination="evil.com"))
        p.add_rule("inst-1", NetworkRule(rule_id="r2", direction="egress", action="allow", destination="*"))
        assert p.check_egress("inst-1", "evil.com") is False
        assert p.check_egress("inst-1", "good.com") is True

    def test_default_deny_with_rules(self):
        p = AppNetworkPolicy()
        p.add_rule("inst-1", NetworkRule(rule_id="r1", direction="egress", action="allow", destination="api.stripe.com"))
        assert p.check_egress("inst-1", "other.com") is False

    def test_port_specific(self):
        p = AppNetworkPolicy()
        p.add_rule("inst-1", NetworkRule(rule_id="r1", direction="egress", action="allow", destination="db.example.com", port=5432))
        assert p.check_egress("inst-1", "db.example.com", port=5432) is True
        assert p.check_egress("inst-1", "db.example.com", port=3306) is False


class TestRemove:
    def test_remove(self):
        p = AppNetworkPolicy()
        p.add_rule("inst-1", NetworkRule(rule_id="r1", direction="egress", action="allow", destination="*"))
        assert p.remove_rule("inst-1", "r1") is True


class TestIsolation:
    def test_cross_installation(self):
        p = AppNetworkPolicy()
        p.add_rule("inst-1", NetworkRule(rule_id="r1", direction="egress", action="allow", destination="api.com"))
        assert p.check_egress("inst-2", "api.com") is True  # no rules = allow
