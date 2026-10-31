import pytest
from app.services.app_api_developer_api_request_validation_report import AppAPIDeveloperAPIRequestValidationReport

class TestValidationReport:
    def test_record(self):
        r = AppAPIDeveloperAPIRequestValidationReport()
        f = r.record("inst-1", "/api/users", "email", "format", "not-email")
        assert f.count == 1

    def test_accumulate(self):
        r = AppAPIDeveloperAPIRequestValidationReport()
        r.record("inst-1", "/api/users", "email", "format")
        r.record("inst-1", "/api/users", "email", "format")
        top = r.top_failures("inst-1")
        assert top[0].count == 2

    def test_by_endpoint(self):
        r = AppAPIDeveloperAPIRequestValidationReport()
        r.record("inst-1", "/api/a", "name", "required")
        r.record("inst-1", "/api/b", "age", "type")
        assert len(r.by_endpoint("inst-1", "/api/a")) == 1

    def test_by_rule(self):
        r = AppAPIDeveloperAPIRequestValidationReport()
        r.record("inst-1", "/a", "x", "required")
        r.record("inst-1", "/a", "y", "required")
        r.record("inst-1", "/a", "z", "type")
        assert r.by_rule("inst-1") == {"required": 2, "type": 1}

    def test_isolation(self):
        r = AppAPIDeveloperAPIRequestValidationReport()
        r.record("inst-1", "/a", "x", "required")
        assert r.total_failures("inst-2") == 0
