import pytest
from app.services.app_api_developer_role import AppAPIDeveloperRole

class TestRole:
    def test_create_assign(self):
        r = AppAPIDeveloperRole()
        r.create_role("inst-1", "admin", "Admin", ["read", "write", "delete"])
        r.assign("inst-1", "alice", "admin")
        assert r.has_permission("inst-1", "alice", "write") is True
        assert r.has_permission("inst-1", "alice", "deploy") is False

    def test_no_role(self):
        r = AppAPIDeveloperRole()
        assert r.has_permission("inst-1", "nobody", "read") is False

    def test_member_count(self):
        r = AppAPIDeveloperRole()
        r.create_role("inst-1", "dev", "Dev", ["read"])
        r.assign("inst-1", "alice", "dev")
        r.assign("inst-1", "bob", "dev")
        assert r.list_roles("inst-1")[0].member_count == 2

    def test_isolation(self):
        r = AppAPIDeveloperRole()
        r.create_role("inst-1", "admin", "Admin", ["all"])
        assert r.list_roles("inst-2") == []
