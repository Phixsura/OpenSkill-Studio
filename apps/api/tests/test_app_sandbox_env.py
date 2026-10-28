"""Tests for App Sandbox Environment — lifecycle, limits, logs, usage."""

import pytest

from app.services.app_sandbox_env import (
    AppSandboxManager,
    ResourceLimits,
    SandboxStatus,
)


class TestCreateSandbox:
    def test_create(self):
        m = AppSandboxManager()
        sb = m.create_sandbox("inst-1", "sb-1", "1.0.0")
        assert sb.sandbox_id == "sb-1"
        assert sb.status == SandboxStatus.CREATING
        assert sb.limits.memory_mb == 256

    def test_custom_limits(self):
        m = AppSandboxManager()
        limits = ResourceLimits(memory_mb=512, cpu_cores=1.0, timeout_seconds=600)
        sb = m.create_sandbox("inst-1", "sb-1", "1.0.0", limits=limits)
        assert sb.limits.memory_mb == 512

    def test_duplicate(self):
        m = AppSandboxManager()
        m.create_sandbox("inst-1", "sb-1", "1.0.0")
        with pytest.raises(ValueError, match="already exists"):
            m.create_sandbox("inst-1", "sb-1", "1.0.0")

    def test_missing_version(self):
        m = AppSandboxManager()
        with pytest.raises(ValueError, match="app_version"):
            m.create_sandbox("inst-1", "sb-1", "")

    def test_max_per_installation(self):
        m = AppSandboxManager(max_per_installation=2)
        m.create_sandbox("inst-1", "sb-1", "1.0.0")
        m.create_sandbox("inst-1", "sb-2", "1.0.0")
        with pytest.raises(ValueError, match="Maximum"):
            m.create_sandbox("inst-1", "sb-3", "1.0.0")

    def test_stopped_doesnt_count_toward_limit(self):
        m = AppSandboxManager(max_per_installation=2)
        m.create_sandbox("inst-1", "sb-1", "1.0.0")
        m.start_sandbox("inst-1", "sb-1")
        m.stop_sandbox("inst-1", "sb-1")
        m.create_sandbox("inst-1", "sb-2", "1.0.0")
        m.create_sandbox("inst-1", "sb-3", "1.0.0")  # sb-1 stopped, so only sb-2,sb-3 active
        assert len(m.list_sandboxes("inst-1")) == 3


class TestLifecycle:
    def test_full_lifecycle(self):
        m = AppSandboxManager()
        m.create_sandbox("inst-1", "sb-1", "1.0.0")
        m.start_sandbox("inst-1", "sb-1")
        sb = m.stop_sandbox("inst-1", "sb-1", exit_code=0)
        assert sb.status == SandboxStatus.STOPPED
        assert sb.exit_code == 0

    def test_cannot_start_running(self):
        m = AppSandboxManager()
        m.create_sandbox("inst-1", "sb-1", "1.0.0")
        m.start_sandbox("inst-1", "sb-1")
        with pytest.raises(ValueError, match="Cannot start"):
            m.start_sandbox("inst-1", "sb-1")

    def test_cannot_stop_creating(self):
        m = AppSandboxManager()
        m.create_sandbox("inst-1", "sb-1", "1.0.0")
        with pytest.raises(ValueError, match="Cannot stop"):
            m.stop_sandbox("inst-1", "sb-1")

    def test_terminate_running(self):
        m = AppSandboxManager()
        m.create_sandbox("inst-1", "sb-1", "1.0.0")
        m.start_sandbox("inst-1", "sb-1")
        sb = m.terminate_sandbox("inst-1", "sb-1")
        assert sb.status == SandboxStatus.TERMINATED

    def test_terminate_creating(self):
        m = AppSandboxManager()
        m.create_sandbox("inst-1", "sb-1", "1.0.0")
        sb = m.terminate_sandbox("inst-1", "sb-1")
        assert sb.status == SandboxStatus.TERMINATED

    def test_double_terminate(self):
        m = AppSandboxManager()
        m.create_sandbox("inst-1", "sb-1", "1.0.0")
        m.terminate_sandbox("inst-1", "sb-1")
        with pytest.raises(ValueError, match="already terminated"):
            m.terminate_sandbox("inst-1", "sb-1")


class TestLogs:
    def test_append_and_get(self):
        m = AppSandboxManager()
        m.create_sandbox("inst-1", "sb-1", "1.0.0")
        m.append_log("inst-1", "sb-1", "Starting app...")
        m.append_log("inst-1", "sb-1", "Listening on :8080")
        logs = m.get_logs("inst-1", "sb-1")
        assert len(logs) == 2
        assert logs[0] == "Starting app..."

    def test_tail_logs(self):
        m = AppSandboxManager()
        m.create_sandbox("inst-1", "sb-1", "1.0.0")
        for i in range(10):
            m.append_log("inst-1", "sb-1", f"line-{i}")
        logs = m.get_logs("inst-1", "sb-1", tail=3)
        assert len(logs) == 3
        assert logs[0] == "line-7"


class TestUsage:
    def test_update_usage(self):
        m = AppSandboxManager()
        m.create_sandbox("inst-1", "sb-1", "1.0.0")
        sb = m.update_usage("inst-1", "sb-1", memory_mb=128.5, cpu_seconds=45.2)
        assert sb.memory_used_mb == 128.5
        assert sb.cpu_used_seconds == 45.2

    def test_negative_clamped(self):
        m = AppSandboxManager()
        m.create_sandbox("inst-1", "sb-1", "1.0.0")
        sb = m.update_usage("inst-1", "sb-1", memory_mb=-10)
        assert sb.memory_used_mb == 0.0


class TestIsolation:
    def test_cross_installation(self):
        m = AppSandboxManager()
        m.create_sandbox("inst-1", "sb-1", "1.0.0")
        with pytest.raises(KeyError):
            m.get_sandbox("inst-2", "sb-1")

    def test_list_scoped(self):
        m = AppSandboxManager()
        m.create_sandbox("inst-1", "sb-1", "1.0.0")
        m.create_sandbox("inst-2", "sb-2", "1.0.0")
        assert len(m.list_sandboxes("inst-1")) == 1
