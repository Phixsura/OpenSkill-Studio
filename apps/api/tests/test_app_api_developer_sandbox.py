import pytest
from app.services.app_api_developer_sandbox import AppAPIDeveloperSandbox

class TestSandbox:
    def test_create(self):
        s = AppAPIDeveloperSandbox()
        sb = s.create("inst-1", "sb1", "alice", "https://sandbox-1.api.dev")
        assert sb.api_key.startswith("sb_")
        assert sb.active is True

    def test_duplicate(self):
        s = AppAPIDeveloperSandbox()
        s.create("inst-1", "sb1", "alice", "https://x")
        with pytest.raises(ValueError):
            s.create("inst-1", "sb1", "bob", "https://y")

    def test_deactivate(self):
        s = AppAPIDeveloperSandbox()
        s.create("inst-1", "sb1", "alice", "https://x")
        s.deactivate("inst-1", "sb1")
        assert s.active_sandboxes("inst-1") == []

    def test_request_count(self):
        s = AppAPIDeveloperSandbox()
        s.create("inst-1", "sb1", "alice", "https://x")
        s.record_request("inst-1", "sb1")
        assert s.list_sandboxes("inst-1")[0].request_count == 1

    def test_isolation(self):
        s = AppAPIDeveloperSandbox()
        s.create("inst-1", "sb1", "alice", "https://x")
        assert s.list_sandboxes("inst-2") == []
