import pytest
from app.services.app_api_developer_api_api_compliance_report import AppAPIDeveloperAPIApiComplianceReport

class TestComplianceReport:
    def test_add_check(self):
        r = AppAPIDeveloperAPIApiComplianceReport()
        c = r.add_check("inst-1", "c1", "SOC2", "Access controls")
        assert c.framework == "SOC2"

    def test_invalid_framework(self):
        r = AppAPIDeveloperAPIApiComplianceReport()
        with pytest.raises(ValueError):
            r.add_check("inst-1", "c1", "INVALID", "test")

    def test_compliance_rate(self):
        r = AppAPIDeveloperAPIApiComplianceReport()
        r.add_check("inst-1", "c1", "SOC2", "Access")
        r.add_check("inst-1", "c2", "SOC2", "Encryption")
        r.update_status("inst-1", "c1", "compliant")
        r.update_status("inst-1", "c2", "non_compliant")
        assert r.compliance_rate("inst-1", "SOC2") == 50.0

    def test_by_framework(self):
        r = AppAPIDeveloperAPIApiComplianceReport()
        r.add_check("inst-1", "c1", "SOC2", "A")
        r.add_check("inst-1", "c2", "GDPR", "B")
        r.update_status("inst-1", "c1", "compliant")
        fw = r.by_framework("inst-1")
        assert "SOC2" in fw
        assert fw["SOC2"]["compliant"] == 1

    def test_isolation(self):
        r = AppAPIDeveloperAPIApiComplianceReport()
        r.add_check("inst-1", "c1", "SOC2", "A")
        assert len(r.non_compliant("inst-2")) == 0
