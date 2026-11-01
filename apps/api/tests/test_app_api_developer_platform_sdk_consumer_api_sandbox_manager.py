"""Tests for Consumer Sandbox Manager service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_sandbox_manager import SandboxManager


class TestSandboxManager:
    def test_create_sandbox(self):
        svc = SandboxManager()
        result = svc.create("c1", "Test Sandbox")
        assert result["sandbox_id"].startswith("sb-")
        assert result["api_key"].startswith("sb_")

    def test_use_request(self):
        svc = SandboxManager()
        result = svc.create("c1", "Test", max_requests=5)
        sid = result["sandbox_id"]
        r = svc.use_request(sid)
        assert r["allowed"] is True
        assert r["remaining"] == 4

    def test_quota_exceeded(self):
        svc = SandboxManager()
        result = svc.create("c1", "Tiny", max_requests=2)
        sid = result["sandbox_id"]
        svc.use_request(sid)
        svc.use_request(sid)
        r = svc.use_request(sid)
        assert r["allowed"] is False
        assert r["reason"] == "quota_exceeded"

    def test_pause_resume(self):
        svc = SandboxManager()
        sid = svc.create("c1", "Test")["sandbox_id"]
        svc.pause(sid)
        r = svc.use_request(sid)
        assert r["allowed"] is False
        svc.resume(sid)
        r = svc.use_request(sid)
        assert r["allowed"] is True

    def test_reset(self):
        svc = SandboxManager()
        result = svc.create("c1", "Test", max_requests=3)
        sid = result["sandbox_id"]
        old_key = result["api_key"]
        svc.use_request(sid)
        svc.use_request(sid)
        reset_result = svc.reset(sid)
        assert reset_result["new_api_key"] != old_key
        sb = svc.get_sandbox(sid)
        assert sb["request_count"] == 0

    def test_delete(self):
        svc = SandboxManager()
        sid = svc.create("c1", "Test")["sandbox_id"]
        assert svc.delete(sid)["deleted"] is True
        assert svc.get_sandbox(sid) is None

    def test_list_by_consumer(self):
        svc = SandboxManager()
        svc.create("c1", "A")
        svc.create("c1", "B")
        svc.create("c2", "C")
        assert len(svc.list_sandboxes("c1")) == 2

    def test_stats(self):
        svc = SandboxManager()
        sid = svc.create("c1", "A")["sandbox_id"]
        svc.create("c1", "B")
        svc.use_request(sid)
        svc.pause(svc.create("c1", "C")["sandbox_id"])
        stats = svc.get_stats()
        assert stats["total"] == 3
        assert stats["paused"] == 1
        assert stats["total_requests"] == 1

    def test_not_found(self):
        svc = SandboxManager()
        assert svc.use_request("missing")["reason"] == "not_found"

    def test_invalid_max_requests(self):
        svc = SandboxManager()
        with pytest.raises(ValueError):
            svc.create("c1", "Bad", max_requests=0)

    def test_isolation(self):
        a, b = SandboxManager(), SandboxManager()
        a.create("c1", "Test")
        assert b.list_sandboxes() == []
