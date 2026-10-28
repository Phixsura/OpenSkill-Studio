"""Tests for App Compliance Checker — rules, checks, reports."""

import pytest

from app.services.app_compliance_checker import (
    AppComplianceChecker,
    ComplianceRule,
)


@pytest.fixture
def checker():
    c = AppComplianceChecker()
    c.add_rule(ComplianceRule(
        rule_id="r1", name="Privacy Policy Required",
        description="Must have a privacy_url",
        check_type="required_field", target="privacy_url",
    ))
    c.add_rule(ComplianceRule(
        rule_id="r2", name="No Eval",
        description="eval() is banned",
        check_type="banned_pattern", target=r"eval\(",
        severity="error",
    ))
    c.add_rule(ComplianceRule(
        rule_id="r3", name="Description Length",
        description="Description max 500 chars",
        check_type="max_size", target="description:500",
        severity="warning",
    ))
    return c


class TestAddRule:
    def test_add(self, checker):
        assert len(checker.list_rules()) == 3

    def test_duplicate(self, checker):
        with pytest.raises(ValueError, match="already exists"):
            checker.add_rule(ComplianceRule(rule_id="r1", name="X", description="X",
                                           check_type="required_field", target="x"))

    def test_missing_id(self):
        c = AppComplianceChecker()
        with pytest.raises(ValueError, match="rule_id"):
            c.add_rule(ComplianceRule(rule_id="", name="X", description="X",
                                     check_type="required_field", target="x"))


class TestRemoveRule:
    def test_remove(self, checker):
        assert checker.remove_rule("r1") is True
        assert len(checker.list_rules()) == 2

    def test_remove_nonexistent(self, checker):
        assert checker.remove_rule("nope") is False


class TestRequiredField:
    def test_present(self, checker):
        report = checker.check("inst-1", {
            "privacy_url": "https://example.com/privacy",
            "description": "Short desc",
        })
        assert not any(v.rule_id == "r1" for v in report.violations)

    def test_missing(self, checker):
        report = checker.check("inst-1", {"description": "desc"})
        assert any(v.rule_id == "r1" for v in report.violations)

    def test_empty(self, checker):
        report = checker.check("inst-1", {"privacy_url": "", "description": "x"})
        assert any(v.rule_id == "r1" for v in report.violations)


class TestBannedPattern:
    def test_no_violation(self, checker):
        report = checker.check("inst-1", {
            "privacy_url": "https://x.com",
            "code": "console.log('safe')",
        })
        assert not any(v.rule_id == "r2" for v in report.violations)

    def test_violation(self, checker):
        report = checker.check("inst-1", {
            "privacy_url": "https://x.com",
            "code": "eval('dangerous')",
        })
        assert any(v.rule_id == "r2" for v in report.violations)


class TestMaxSize:
    def test_within_limit(self, checker):
        report = checker.check("inst-1", {
            "privacy_url": "https://x.com",
            "description": "Short",
        })
        assert not any(v.rule_id == "r3" for v in report.violations)

    def test_exceeds_limit(self, checker):
        report = checker.check("inst-1", {
            "privacy_url": "https://x.com",
            "description": "x" * 501,
        })
        assert any(v.rule_id == "r3" for v in report.violations)


class TestReport:
    def test_compliant(self, checker):
        report = checker.check("inst-1", {
            "privacy_url": "https://x.com",
            "description": "Good app",
        })
        assert report.compliant is True
        assert report.rules_checked == 3

    def test_non_compliant(self, checker):
        report = checker.check("inst-1", {})
        assert report.compliant is False
        assert report.error_count >= 1

    def test_warning_still_compliant(self):
        c = AppComplianceChecker()
        c.add_rule(ComplianceRule(
            rule_id="w1", name="Warn", description="x",
            check_type="max_size", target="name:5",
            severity="warning",
        ))
        report = c.check("inst-1", {"name": "toolong"})
        assert report.compliant is True
        assert report.warning_count == 1


class TestIsolation:
    def test_missing_installation_id(self, checker):
        with pytest.raises(ValueError):
            checker.check("", {})
