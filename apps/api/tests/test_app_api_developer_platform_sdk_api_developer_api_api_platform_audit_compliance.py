from app.services.app_api_developer_platform_sdk_api_developer_api_api_platform_audit_compliance import AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformAuditCompliance

class TestAuditCompliance:
    def test_add_framework(self):
        c = AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformAuditCompliance()
        f = c.add_framework("inst-1", "SOC2", 100, compliant=95, non_compliant=3)
        assert f.compliance_pct == 96.9
        assert f.not_assessed == 2

    def test_audit_ready(self):
        c = AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformAuditCompliance()
        c.add_framework("inst-1", "SOC2", 100, compliant=96, non_compliant=2)
        assert len(c.audit_ready_frameworks("inst-1")) == 1

    def test_not_ready(self):
        c = AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformAuditCompliance()
        c.add_framework("inst-1", "SOC2", 100, compliant=50, non_compliant=10)
        assert len(c.audit_ready_frameworks("inst-1")) == 0

    def test_overall(self):
        c = AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformAuditCompliance()
        c.add_framework("inst-1", "SOC2", 100, compliant=90, non_compliant=10)
        c.add_framework("inst-1", "GDPR", 50, compliant=45, non_compliant=5)
        assert c.overall_compliance("inst-1") == 90.0

    def test_isolation(self):
        c = AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformAuditCompliance()
        c.add_framework("inst-1", "SOC2", 100, compliant=95)
        assert len(c.all_frameworks("inst-2")) == 0
