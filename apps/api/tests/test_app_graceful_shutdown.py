"""Tests for App Graceful Shutdown — phases, draining, hooks."""

import pytest

from app.services.app_graceful_shutdown import AppGracefulShutdown, ShutdownPhase


class TestRegister:
    def test_register(self):
        g = AppGracefulShutdown()
        s = g.register("inst-1", drain_timeout_seconds=60, hooks_count=3)
        assert s.phase == ShutdownPhase.RUNNING
        assert s.hooks_registered == 3

    def test_invalid_timeout(self):
        g = AppGracefulShutdown()
        with pytest.raises(ValueError):
            g.register("inst-1", drain_timeout_seconds=0)


class TestShutdownLifecycle:
    def test_initiate(self):
        g = AppGracefulShutdown()
        g.register("inst-1", hooks_count=0)
        s = g.initiate_shutdown("inst-1", in_flight=5, now=1000.0)
        assert s.phase == ShutdownPhase.DRAINING
        assert s.in_flight_requests == 5

    def test_complete(self):
        g = AppGracefulShutdown()
        g.register("inst-1", hooks_count=0)
        g.initiate_shutdown("inst-1")
        s = g.complete_shutdown("inst-1")
        assert s.phase == ShutdownPhase.SHUTDOWN

    def test_cannot_initiate_twice(self):
        g = AppGracefulShutdown()
        g.register("inst-1")
        g.initiate_shutdown("inst-1")
        with pytest.raises(ValueError):
            g.initiate_shutdown("inst-1")


class TestDraining:
    def test_ready_when_drained(self):
        g = AppGracefulShutdown()
        g.register("inst-1", hooks_count=1)
        g.initiate_shutdown("inst-1", in_flight=0)
        g.complete_hook("inst-1")
        assert g.is_ready_to_shutdown("inst-1") is True

    def test_not_ready_with_in_flight(self):
        g = AppGracefulShutdown()
        g.register("inst-1", drain_timeout_seconds=60, hooks_count=0)
        g.initiate_shutdown("inst-1", in_flight=5, now=1000.0)
        assert g.is_ready_to_shutdown("inst-1", now=1010.0) is False

    def test_ready_after_timeout(self):
        g = AppGracefulShutdown()
        g.register("inst-1", drain_timeout_seconds=10, hooks_count=0)
        g.initiate_shutdown("inst-1", in_flight=5, now=1000.0)
        assert g.is_ready_to_shutdown("inst-1", now=1011.0) is True

    def test_hooks_must_complete(self):
        g = AppGracefulShutdown()
        g.register("inst-1", hooks_count=2)
        g.initiate_shutdown("inst-1", in_flight=0)
        g.complete_hook("inst-1")
        assert g.is_ready_to_shutdown("inst-1") is False
        g.complete_hook("inst-1")
        assert g.is_ready_to_shutdown("inst-1") is True


class TestIsolation:
    def test_cross_installation(self):
        g = AppGracefulShutdown()
        g.register("inst-1")
        with pytest.raises(KeyError):
            g.get_state("inst-2")
