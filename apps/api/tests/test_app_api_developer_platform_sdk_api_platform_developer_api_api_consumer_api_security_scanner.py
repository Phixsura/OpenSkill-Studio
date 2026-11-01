from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_security_scanner import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiSecurityScanner, SecurityFinding, ScanSeverity,
)

class TestSecurityScanner:
    def test_scan_and_score(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiSecurityScanner()
        findings = [SecurityFinding(finding_id="f1", category="auth", severity=ScanSeverity.HIGH, title="No API key rotation")]
        result = svc.run_scan("inst-1", "s1", "c1", findings)
        assert result.score == 85  # 100 - 15

    def test_resolve_improves_score(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiSecurityScanner()
        svc.run_scan("inst-1", "s1", "c1", [SecurityFinding(finding_id="f1", category="encryption", severity=ScanSeverity.CRITICAL, title="No TLS")])
        assert svc.get_score("inst-1", "c1") == 75
        svc.resolve_finding("inst-1", "c1", "f1")
        assert svc.get_score("inst-1", "c1") == 100

    def test_at_risk(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiSecurityScanner()
        svc.run_scan("inst-1", "s1", "c1", [SecurityFinding(finding_id="f1", category="auth", severity=ScanSeverity.CRITICAL, title="X"), SecurityFinding(finding_id="f2", category="headers", severity=ScanSeverity.CRITICAL, title="Y")])
        assert "c1" in svc.consumers_at_risk("inst-1", 70)

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiSecurityScanner()
        svc.run_scan("inst-1", "s1", "c1", [])
        assert len(svc.list_scans("inst-2")) == 0
