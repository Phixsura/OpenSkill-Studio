import pytest
from app.services.app_api_developer_quickstart import AppAPIDeveloperQuickstart

STEPS = [{"step_id": "s1", "title": "Install SDK", "code": "npm install"}, {"step_id": "s2", "title": "Auth", "code": "sdk.auth()"}]

class TestQuickstart:
    def test_start(self):
        q = AppAPIDeveloperQuickstart()
        p = q.start("inst-1", "alice", "javascript", STEPS)
        assert p.completion_pct == 0.0

    def test_complete(self):
        q = AppAPIDeveloperQuickstart()
        q.start("inst-1", "alice", "python", STEPS)
        q.complete_step("inst-1", "alice", "s1")
        assert q.get_progress("inst-1", "alice").completion_pct == 50.0

    def test_full(self):
        q = AppAPIDeveloperQuickstart()
        q.start("inst-1", "alice", "go", STEPS)
        q.complete_step("inst-1", "alice", "s1")
        q.complete_step("inst-1", "alice", "s2")
        assert q.get_progress("inst-1", "alice").completion_pct == 100.0
