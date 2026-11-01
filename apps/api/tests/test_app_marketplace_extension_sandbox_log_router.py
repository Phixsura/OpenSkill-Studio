from app.services.app_marketplace_extension_sandbox_log_router import (
    SandboxLogRouterService, LogLevel, DestinationType,
)
import pytest


def test_add_and_route():
    svc = SandboxLogRouterService()
    svc.add_destination("sb-1", "console", "Console", DestinationType.CONSOLE)
    result = svc.route("sb-1", LogLevel.INFO, "Server started")
    assert "console" in result.destinations


def test_level_filtering():
    svc = SandboxLogRouterService()
    svc.add_destination("sb-1", "errors", "Error Log", DestinationType.FILE,
                        min_level=LogLevel.ERROR)
    svc.add_destination("sb-1", "all", "All Logs", DestinationType.CONSOLE)

    r1 = svc.route("sb-1", LogLevel.DEBUG, "debug msg")
    assert "errors" not in r1.destinations
    assert "all" in r1.destinations

    r2 = svc.route("sb-1", LogLevel.ERROR, "error msg")
    assert "errors" in r2.destinations
    assert "all" in r2.destinations


def test_disabled_destination():
    svc = SandboxLogRouterService()
    svc.add_destination("sb-1", "d1", "Test", DestinationType.CONSOLE)
    svc.toggle("sb-1", "d1")
    result = svc.route("sb-1", LogLevel.INFO, "msg")
    assert len(result.destinations) == 0


def test_multiple_destinations():
    svc = SandboxLogRouterService()
    svc.add_destination("sb-1", "console", "Console", DestinationType.CONSOLE)
    svc.add_destination("sb-1", "webhook", "Slack", DestinationType.WEBHOOK)
    svc.add_destination("sb-1", "agg", "Datadog", DestinationType.AGGREGATOR)
    result = svc.route("sb-1", LogLevel.WARN, "warning")
    assert len(result.destinations) == 3


def test_remove():
    svc = SandboxLogRouterService()
    svc.add_destination("sb-1", "tmp", "Temp", DestinationType.CONSOLE)
    assert svc.remove("sb-1", "tmp") is True
    assert len(svc.list_destinations("sb-1")) == 0


def test_duplicate_rejected():
    svc = SandboxLogRouterService()
    svc.add_destination("sb-1", "d1", "A", DestinationType.CONSOLE)
    with pytest.raises(ValueError, match="already exists"):
        svc.add_destination("sb-1", "d1", "B", DestinationType.WEBHOOK)


def test_stats():
    svc = SandboxLogRouterService()
    svc.add_destination("sb-1", "c", "Console", DestinationType.CONSOLE)
    svc.add_destination("sb-1", "w", "Webhook", DestinationType.WEBHOOK)
    svc.route("sb-1", LogLevel.INFO, "msg")
    stats = svc.get_stats("sb-1")
    assert stats["total"] == 2
    assert stats["total_routed"] == 2
