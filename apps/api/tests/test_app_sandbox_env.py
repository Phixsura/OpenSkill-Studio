"""Tests for App Sandbox Environment — create, lifecycle, limits."""

import pytest

from app.services.app_sandbox_env import AppSandboxEnv, SandboxStatus


class TestCreate:
    def test_create(self):
        s = AppSandboxEnv()
        sb = s.create("inst-1", "sb1", "Dev Sandbox", memory_mb=1024)
        assert sb.status == SandboxStatus.CREATING

    def test_low_memory(self):
        s = AppSandboxEnv()
        with pytest.raises(ValueError, match="128"):
            s.create("inst-1", "sb1", "Bad", memory_mb=64)

    def test_duplicate(self):
        s = AppSandboxEnv()
        s.create("inst-1", "sb1", "A")
        with pytest.raises(ValueError, match="already exists"):
            s.create("inst-1", "sb1", "B")


class TestLifecycle:
    def test_start_stop(self):
        s = AppSandboxEnv()
        s.create("inst-1", "sb1", "Dev")
        s.start("inst-1", "sb1")
        sb = s.stop("inst-1", "sb1")
        assert sb.status == SandboxStatus.STOPPED

    def test_running_count(self):
        s = AppSandboxEnv()
        s.create("inst-1", "sb1", "A")
        s.create("inst-1", "sb2", "B")
        s.start("inst-1", "sb1")
        assert s.running_count("inst-1") == 1


class TestIsolation:
    def test_cross(self):
        s = AppSandboxEnv()
        s.create("inst-1", "sb1", "Dev")
        assert s.list_sandboxes("inst-2") == []
