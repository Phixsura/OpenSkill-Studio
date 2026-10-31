from app.services.app_marketplace_extension_cqrs_bus import (
    CqrsCommandBusService, Command, Query
)


def test_dispatch_command():
    bus = CqrsCommandBusService()
    bus.register_command("create_user", lambda p: {"id": "u1", "name": p["name"]})
    result = bus.dispatch(Command("create_user", {"name": "Alice"}))
    assert result.success is True
    assert result.data["name"] == "Alice"


def test_unregistered_command():
    bus = CqrsCommandBusService()
    result = bus.dispatch(Command("unknown", {}))
    assert result.success is False
    assert "No handler" in result.error


def test_idempotency():
    bus = CqrsCommandBusService()
    call_count = 0
    def handler(p):
        nonlocal call_count
        call_count += 1
        return {"ok": True}
    bus.register_command("pay", handler)
    cmd = Command("pay", {"amount": 100}, idempotency_key="pay-123")
    bus.dispatch(cmd)
    bus.dispatch(cmd)  # duplicate
    assert call_count == 1  # handler called only once


def test_pre_middleware_rejection():
    bus = CqrsCommandBusService()
    bus.register_command("action", lambda p: {"ok": True})
    bus.add_pre_middleware(lambda cmd: "forbidden" if cmd.payload.get("admin") else None)
    result = bus.dispatch(Command("action", {"admin": True}))
    assert result.success is False
    assert "forbidden" in result.error


def test_post_middleware():
    log = []
    bus = CqrsCommandBusService()
    bus.register_command("log_test", lambda p: {"ok": True})
    bus.add_post_middleware(lambda cmd, res: log.append(cmd.command_type))
    bus.dispatch(Command("log_test", {}))
    assert log == ["log_test"]


def test_handler_exception():
    bus = CqrsCommandBusService()
    bus.register_command("fail", lambda p: (_ for _ in ()).throw(RuntimeError("boom")))
    result = bus.dispatch(Command("fail", {}))
    assert result.success is False
    assert "boom" in result.error
    assert len(bus.get_dead_letters()) == 1


def test_query():
    bus = CqrsCommandBusService()
    bus.register_query("get_users", lambda p: {"users": ["Alice", "Bob"]})
    result = bus.query(Query("get_users"))
    assert result["users"] == ["Alice", "Bob"]


def test_query_unregistered():
    bus = CqrsCommandBusService()
    try:
        bus.query(Query("unknown"))
        assert False
    except ValueError:
        pass


def test_history():
    bus = CqrsCommandBusService()
    bus.register_command("op", lambda p: {})
    bus.dispatch(Command("op", {}))
    bus.dispatch(Command("op", {}))
    history = bus.get_history()
    assert len(history) == 2
    assert all(h["success"] for h in history)


def test_duplicate_registration():
    bus = CqrsCommandBusService()
    bus.register_command("op", lambda p: {})
    try:
        bus.register_command("op", lambda p: {})
        assert False
    except ValueError:
        pass
