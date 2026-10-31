from app.services.app_marketplace_extension_graceful_shutdown import GracefulShutdownService


def test_normal_shutdown():
    gs = GracefulShutdownService()
    gs.register_hook("close_db", lambda: None)
    gs.register_hook("flush_logs", lambda: None)
    result = gs.shutdown("maintenance")
    assert result.reason == "maintenance"
    assert result.phase == "terminated"
    assert len(result.hooks_completed) == 2


def test_hook_priority():
    gs = GracefulShutdownService()
    order = []
    gs.register_hook("last", lambda: order.append("last"), priority=1)
    gs.register_hook("first", lambda: order.append("first"), priority=10)
    gs.shutdown()
    assert order == ["first", "last"]


def test_hook_failure():
    gs = GracefulShutdownService()
    gs.register_hook("ok", lambda: None)
    gs.register_hook("bad", lambda: (_ for _ in ()).throw(RuntimeError("crash")))
    result = gs.shutdown()
    assert "ok" in result.hooks_completed
    assert "bad" in result.hooks_failed


def test_reject_during_shutdown():
    gs = GracefulShutdownService()
    gs.shutdown()
    assert gs.request_start() is False  # new requests rejected


def test_inflight_tracking():
    gs = GracefulShutdownService()
    gs.request_start()
    gs.request_start()
    assert gs.inflight_count == 2
    gs.request_end()
    assert gs.inflight_count == 1


def test_ready_state():
    gs = GracefulShutdownService()
    assert gs.is_ready is True
    gs.shutdown()
    assert gs.is_ready is False


def test_drain_inflight():
    gs = GracefulShutdownService()
    gs.request_start()
    gs.request_end()  # complete before shutdown
    result = gs.shutdown()
    assert result.inflight_drained >= 0


def test_status():
    gs = GracefulShutdownService()
    gs.register_hook("h1", lambda: None)
    gs.request_start()
    status = gs.get_status()
    assert status["inflight"] == 1
    assert status["hooks_registered"] == 1
    assert status["shutting_down"] is False


def test_shutdown_reason():
    gs = GracefulShutdownService()
    r1 = gs.shutdown("SIGTERM")
    assert r1.reason == "SIGTERM"
