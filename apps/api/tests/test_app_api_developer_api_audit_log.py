import pytest
from app.services.app_api_developer_api_audit_log import AppAPIDeveloperAPIAuditLog

class TestAuditLog:
    def test_log(self):
        a = AppAPIDeveloperAPIAuditLog()
        e = a.log("inst-1", "e1", "user@example.com", "create", "api_key", "k1", ip_address="1.2.3.4")
        assert e.action == "create"

    def test_invalid_action(self):
        a = AppAPIDeveloperAPIAuditLog()
        with pytest.raises(ValueError):
            a.log("inst-1", "e1", "user", "hack", "key", "k1")

    def test_query_by_actor(self):
        a = AppAPIDeveloperAPIAuditLog()
        a.log("inst-1", "e1", "alice", "create", "key", "k1")
        a.log("inst-1", "e2", "bob", "delete", "key", "k2")
        assert len(a.query("inst-1", actor="alice")) == 1

    def test_query_by_action(self):
        a = AppAPIDeveloperAPIAuditLog()
        a.log("inst-1", "e1", "alice", "create", "key", "k1")
        a.log("inst-1", "e2", "alice", "delete", "key", "k2")
        assert len(a.query("inst-1", action="delete")) == 1

    def test_isolation(self):
        a = AppAPIDeveloperAPIAuditLog()
        a.log("inst-1", "e1", "alice", "create", "key", "k1")
        assert a.count("inst-2") == 0
