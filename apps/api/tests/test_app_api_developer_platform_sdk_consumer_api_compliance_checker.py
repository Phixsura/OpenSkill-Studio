"""Tests for Endpoint Compliance Checker service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_compliance_checker import (
    ComplianceChecker, ComplianceRule,
)


class TestComplianceChecker:
    def _setup(self):
        svc = ComplianceChecker()
        svc.add_rule(ComplianceRule("r1", "gdpr", "Data encryption", severity="critical"))
        svc.add_rule(ComplianceRule("r2", "gdpr", "Consent tracking", severity="high"))
        svc.add_rule(ComplianceRule("r3", "soc2", "Access logging", severity="medium"))
        return svc

    def test_check_pass(self):
        svc = self._setup()
        result = svc.check("ep1", "r1", True)
        assert result["passed"] is True
        assert result["framework"] == "gdpr"

    def test_check_violation(self):
        svc = self._setup()
        svc.check("ep1", "r1", False, "Missing TLS")
        compliance = svc.get_endpoint_compliance("ep1")
        assert compliance["status"] == "non_compliant"
        assert len(compliance["violations"]) == 1

    def test_full_compliance(self):
        svc = self._setup()
        svc.check("ep1", "r1", True)
        svc.check("ep1", "r2", True)
        svc.check("ep1", "r3", True)
        compliance = svc.get_endpoint_compliance("ep1")
        assert compliance["status"] == "compliant"
        assert compliance["score"] == 100.0

    def test_partial_compliance(self):
        svc = self._setup()
        svc.check("ep1", "r1", True)
        svc.check("ep1", "r2", True)
        svc.check("ep1", "r3", True)
        svc.check("ep1", "r1", True)  # update existing
        # Now fail one - add r4 for 75% compliance
        svc.add_rule(ComplianceRule("r4", "pci_dss", "PCI check"))
        svc.add_rule(ComplianceRule("r5", "ccpa", "CCPA check"))
        svc.check("ep1", "r4", False)
        svc.check("ep1", "r5", True)
        compliance = svc.get_endpoint_compliance("ep1")
        assert compliance["status"] == "partial"

    def test_framework_summary(self):
        svc = self._setup()
        svc.check("ep1", "r1", True)
        svc.check("ep1", "r2", False)
        summary = svc.get_framework_summary("gdpr")
        assert summary["total_rules"] == 2
        assert summary["passed"] == 1
        assert summary["failed"] == 1

    def test_violations_sorted_by_severity(self):
        svc = self._setup()
        svc.check("ep1", "r3", False)  # medium
        svc.check("ep1", "r1", False)  # critical
        compliance = svc.get_endpoint_compliance("ep1")
        assert compliance["violations"][0]["severity"] == "critical"

    def test_unchecked_endpoint(self):
        svc = self._setup()
        assert svc.get_endpoint_compliance("missing")["status"] == "unchecked"

    def test_list_rules(self):
        svc = self._setup()
        gdpr_rules = svc.list_rules(framework="gdpr")
        assert len(gdpr_rules) == 2

    def test_invalid_framework(self):
        svc = ComplianceChecker()
        with pytest.raises(ValueError):
            svc.add_rule(ComplianceRule("r1", "fake_framework", "test"))

    def test_stats(self):
        svc = self._setup()
        svc.check("ep1", "r1", True)
        svc.check("ep1", "r2", False)
        stats = svc.get_stats()
        assert stats["total_checks"] == 2
        assert stats["total_violations"] == 1

    def test_isolation(self):
        a = self._setup()
        b = ComplianceChecker()
        a.check("ep1", "r1", True)
        assert b.get_stats()["total_checks"] == 0
