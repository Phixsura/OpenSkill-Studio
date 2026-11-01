from app.services.app_api_developer_api_api_webhook_security_scanner import AppAPIDeveloperAPIApiWebhookSecurityScanner

class TestSecurityScanner:
    def test_clean_scan(self):
        s = AppAPIDeveloperAPIApiWebhookSecurityScanner()
        findings = s.scan("inst-1", "https://a.com", secret="a" * 32, uses_https=True, signature_algorithm="sha256")
        assert len(findings) == 0

    def test_http_finding(self):
        s = AppAPIDeveloperAPIApiWebhookSecurityScanner()
        findings = s.scan("inst-1", "http://a.com", uses_https=False)
        assert any(f.severity == "critical" for f in findings)

    def test_no_secret(self):
        s = AppAPIDeveloperAPIApiWebhookSecurityScanner()
        findings = s.scan("inst-1", "https://a.com", secret=None)
        assert any(f.category == "auth" for f in findings)

    def test_short_secret(self):
        s = AppAPIDeveloperAPIApiWebhookSecurityScanner()
        findings = s.scan("inst-1", "https://a.com", secret="short")
        assert any("too short" in f.message for f in findings)

    def test_sha1_warning(self):
        s = AppAPIDeveloperAPIApiWebhookSecurityScanner()
        findings = s.scan("inst-1", "https://a.com", secret="a" * 32, signature_algorithm="sha1")
        assert any(f.category == "crypto" for f in findings)

    def test_isolation(self):
        s = AppAPIDeveloperAPIApiWebhookSecurityScanner()
        s.scan("inst-1", "http://a.com", uses_https=False)
        assert s.critical_count("inst-2") == 0
