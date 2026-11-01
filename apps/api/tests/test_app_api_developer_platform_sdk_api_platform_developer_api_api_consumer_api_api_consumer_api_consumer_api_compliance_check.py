import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_compliance_check import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiComplianceCheck, ComplianceRule,
)

class TestConsumerApiComplianceCheck:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_all_pass(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiComplianceCheck()
        svc.add_rule("inst-1", ComplianceRule(rule_id="r1", name="HTTPS Only", category="security"))
        svc.add_rule("inst-1", ComplianceRule(rule_id="r2", name="Auth Required", category="authentication"))
        report = svc.check("inst-1", "c1", {"r1": True, "r2": True}, now=self._now())
        assert report.score == 100.0 and report.failed == 0

    def test_partial_fail(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiComplianceCheck()
        svc.add_rule("inst-1", ComplianceRule(rule_id="r1", name="HTTPS", category="security"))
        svc.add_rule("inst-1", ComplianceRule(rule_id="r2", name="Logging", category="logging"))
        report = svc.check("inst-1", "c1", {"r1": True, "r2": False}, now=self._now())
        assert report.score == 50.0 and report.failed == 1

    def test_missing_check_defaults_false(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiComplianceCheck()
        svc.add_rule("inst-1", ComplianceRule(rule_id="r1", name="X", category="security"))
        report = svc.check("inst-1", "c1", {}, now=self._now())
        assert report.failed == 1

    def test_latest_report(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiComplianceCheck()
        svc.add_rule("inst-1", ComplianceRule(rule_id="r1", name="X", category="security"))
        svc.check("inst-1", "c1", {"r1": False}, now=self._now())
        svc.check("inst-1", "c1", {"r1": True}, now=self._now())
        latest = svc.get_latest("inst-1", "c1")
        assert latest.score == 100.0

    def test_filter_by_category(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiComplianceCheck()
        svc.add_rule("inst-1", ComplianceRule(rule_id="r1", name="X", category="security"))
        svc.add_rule("inst-1", ComplianceRule(rule_id="r2", name="Y", category="logging"))
        assert len(svc.list_rules("inst-1", category="security")) == 1

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiComplianceCheck()
        svc.add_rule("inst-1", ComplianceRule(rule_id="r1", name="X", category="security"))
        assert len(svc.list_rules("inst-2")) == 0
