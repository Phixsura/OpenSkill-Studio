from app.services.app_api_developer_api_security_dashboard import AppAPIDeveloperAPISecurityDashboard

class TestSecurityDashboard:
    def test_update(self):
        d = AppAPIDeveloperAPISecurityDashboard()
        sd = d.update("inst-1", security_score=95, total_findings=10, critical_findings=0)
        assert sd.security_score == 95

    def test_secure(self):
        d = AppAPIDeveloperAPISecurityDashboard()
        d.update("inst-1", security_score=90, critical_findings=0)
        assert d.is_secure("inst-1") is True

    def test_insecure(self):
        d = AppAPIDeveloperAPISecurityDashboard()
        d.update("inst-1", security_score=95, critical_findings=2)
        assert d.is_secure("inst-1") is False

    def test_isolation(self):
        d = AppAPIDeveloperAPISecurityDashboard()
        d.update("inst-1", security_score=50)
        assert d.get("inst-2").security_score == 100.0
