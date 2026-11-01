"""Tests for App Compliance Audit — findings, remediation, score."""

import pytest

from app.services.app_compliance_audit import AppComplianceAudit


class TestAddFinding:
    def test_add(self):
        a = AppComplianceAudit()
        f = a.add_finding("inst-1", "f1", "security", "high", "Exposed API key")
        assert f.severity == "high"
        assert f.remediated is False

    def test_invalid_severity(self):
        a = AppComplianceAudit()
        with pytest.raises(ValueError):
            a.add_finding("inst-1", "f1", "security", "extreme", "Bad")


class TestRemediate:
    def test_remediate(self):
        a = AppComplianceAudit()
        a.add_finding("inst-1", "f1", "security", "high", "Issue")
        f = a.remediate("inst-1", "f1", now=2000.0)
        assert f.remediated is True
        assert f.remediated_at == 2000.0


class TestScore:
    def test_perfect_score(self):
        a = AppComplianceAudit()
        assert a.compliance_score("inst-1") == 100.0

    def test_partial_score(self):
        a = AppComplianceAudit()
        a.add_finding("inst-1", "f1", "security", "high", "A")
        a.add_finding("inst-1", "f2", "security", "low", "B")
        a.remediate("inst-1", "f1")
        assert a.compliance_score("inst-1") == 50.0


class TestList:
    def test_open_only(self):
        a = AppComplianceAudit()
        a.add_finding("inst-1", "f1", "security", "high", "A")
        a.add_finding("inst-1", "f2", "security", "low", "B")
        a.remediate("inst-1", "f1")
        findings = a.list_findings("inst-1", open_only=True)
        assert len(findings) == 1


class TestSeverityCounts:
    def test_counts(self):
        a = AppComplianceAudit()
        a.add_finding("inst-1", "f1", "security", "high", "A")
        a.add_finding("inst-1", "f2", "security", "high", "B")
        a.add_finding("inst-1", "f3", "data", "low", "C")
        counts = a.severity_counts("inst-1")
        assert counts["high"] == 2
        assert counts["low"] == 1


class TestIsolation:
    def test_cross_installation(self):
        a = AppComplianceAudit()
        a.add_finding("inst-1", "f1", "security", "high", "A")
        assert a.list_findings("inst-2") == []
