"""Tests for App API Compliance Check — rules, results, score."""

from app.services.app_api_compliance_check import AppAPIComplianceCheck


class TestRule:
    def test_add(self):
        c = AppAPIComplianceCheck()
        r = c.add_rule("inst-1", "r1", "HTTPS Required", "security")
        assert r.passed is None


class TestResults:
    def test_score(self):
        c = AppAPIComplianceCheck()
        c.add_rule("inst-1", "r1", "HTTPS", "security")
        c.add_rule("inst-1", "r2", "Auth", "security")
        c.add_rule("inst-1", "r3", "Docs", "documentation")
        c.record_result("inst-1", "r1", True)
        c.record_result("inst-1", "r2", True)
        c.record_result("inst-1", "r3", False, "Missing docs")
        assert c.compliance_score("inst-1") == 66.7

    def test_failing(self):
        c = AppAPIComplianceCheck()
        c.add_rule("inst-1", "r1", "HTTPS", "security")
        c.record_result("inst-1", "r1", False)
        assert len(c.failing_rules("inst-1")) == 1


class TestIsolation:
    def test_cross(self):
        c = AppAPIComplianceCheck()
        c.add_rule("inst-1", "r1", "HTTPS", "security")
        assert c.list_rules("inst-2") == []
