import pytest
from app.services.app_api_developer_api_sla_compliance_tracker import AppAPIDeveloperAPISLAComplianceTracker

class TestSLAComplianceTracker:
    def test_set_and_check_compliant(self):
        t = AppAPIDeveloperAPISLAComplianceTracker()
        t.set_target("inst-1", "/api/users", 99.9, 200)
        r = t.check("inst-1", "/api/users", 99.95, 150)
        assert r.compliant is True
        assert r.violations == 0

    def test_non_compliant(self):
        t = AppAPIDeveloperAPISLAComplianceTracker()
        t.set_target("inst-1", "/api/users", 99.9, 200)
        t.check("inst-1", "/api/users", 99.0, 300)
        assert len(t.non_compliant("inst-1")) == 1

    def test_violation_rate(self):
        t = AppAPIDeveloperAPISLAComplianceTracker()
        t.set_target("inst-1", "/a", 99.0, 100)
        t.check("inst-1", "/a", 99.5, 50)
        t.check("inst-1", "/a", 98.0, 50)
        r = t.all_targets("inst-1")[0]
        assert r.violation_rate_pct == 50.0

    def test_isolation(self):
        t = AppAPIDeveloperAPISLAComplianceTracker()
        t.set_target("inst-1", "/a", 99.0, 100)
        assert len(t.all_targets("inst-2")) == 0
