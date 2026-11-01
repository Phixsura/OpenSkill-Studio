import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_compliance_check import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerComplianceCheck, ComplianceRule, ComplianceStatus,
)

class TestConsumerComplianceCheck:
    def test_compliant(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerComplianceCheck()
        svc.add_rule("inst-1", ComplianceRule(rule_id="r1", name="HTTPS only"))
        svc.record_result("inst-1", "c1", "r1", ComplianceStatus.COMPLIANT)
        check = svc.check_consumer("inst-1", "c1")
        assert check["overall"] == "compliant"

    def test_non_compliant(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerComplianceCheck()
        svc.add_rule("inst-1", ComplianceRule(rule_id="r1", name="Rate limiting"))
        svc.record_result("inst-1", "c1", "r1", ComplianceStatus.NON_COMPLIANT, "Exceeded limits")
        check = svc.check_consumer("inst-1", "c1")
        assert check["non_compliant"] == 1

    def test_non_compliant_consumers(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerComplianceCheck()
        svc.add_rule("inst-1", ComplianceRule(rule_id="r1", name="TOS"))
        svc.record_result("inst-1", "c1", "r1", ComplianceStatus.COMPLIANT)
        svc.record_result("inst-1", "c2", "r1", ComplianceStatus.NON_COMPLIANT)
        assert svc.non_compliant_consumers("inst-1") == ["c2"]

    def test_invalid_severity(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerComplianceCheck()
        with pytest.raises(ValueError): svc.add_rule("inst-1", ComplianceRule(rule_id="r1", name="X", severity="extreme"))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerComplianceCheck()
        svc.add_rule("inst-1", ComplianceRule(rule_id="r1", name="X"))
        assert len(svc.list_rules("inst-2")) == 0
