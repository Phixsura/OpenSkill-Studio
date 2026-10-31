from app.services.app_marketplace_extension_command_pattern import CommandPatternService


def test_execute_command():
    svc = CommandPatternService()
    cmd = svc.create_command("set_name",
                             lambda ctx: ctx.update({"name": "Alice"}) or {"name": "Alice"})
    svc.enqueue(cmd)
    ctx = {}
    result = svc.execute_next(ctx)
    assert result.success is True
    assert ctx["name"] == "Alice"


def test_undo():
    svc = CommandPatternService()
    original = {"count": 0}
    cmd = svc.create_command("increment",
                             lambda ctx: ctx.update({"count": ctx["count"] + 1}) or {},
                             lambda ctx: ctx.update({"count": ctx["count"] - 1}))
    svc.enqueue(cmd)
    svc.execute_next(original)
    assert original["count"] == 1
    svc.undo_last(original)
    assert original["count"] == 0


def test_macro_command():
    svc = CommandPatternService()
    c1 = svc.create_command("step1", lambda ctx: ctx.update({"a": 1}) or {"a": 1})
    c2 = svc.create_command("step2", lambda ctx: ctx.update({"b": 2}) or {"b": 2})
    macro = svc.create_macro("setup", [c1, c2])
    ctx = {}
    result = macro.execute(ctx)
    assert result.success is True
    assert ctx["a"] == 1 and ctx["b"] == 2


def test_macro_rollback_on_failure():
    svc = CommandPatternService()
    state = {"x": 0}
    c1 = svc.create_command("inc",
                             lambda ctx: ctx.update({"x": ctx["x"] + 1}) or {},
                             lambda ctx: ctx.update({"x": ctx["x"] - 1}))
    c2 = svc.create_command("fail",
                             lambda ctx: (_ for _ in ()).throw(RuntimeError("boom")))
    macro = svc.create_macro("tx", [c1, c2])
    result = macro.execute(state)
    assert result.success is False
    assert state["x"] == 0  # rolled back


def test_queue_execute_all():
    svc = CommandPatternService()
    for i in range(3):
        svc.enqueue(svc.create_command(f"cmd-{i}", lambda ctx, i=i: {"step": i}))
    ctx = {}
    results = svc.execute_all(ctx)
    assert len(results) == 3
    assert all(r.success for r in results)
    assert svc.pending_count() == 0


def test_history():
    svc = CommandPatternService()
    svc.enqueue(svc.create_command("a", lambda ctx: {}))
    svc.enqueue(svc.create_command("b", lambda ctx: {}))
    svc.execute_all({})
    history = svc.get_history()
    assert len(history) == 2
    assert history[0]["name"] == "a"


def test_no_undo_without_fn():
    svc = CommandPatternService()
    cmd = svc.create_command("no_undo", lambda ctx: {})  # no undo_fn
    svc.enqueue(cmd)
    svc.execute_next({})
    assert svc.undo_last({}) is False


def test_failed_command():
    svc = CommandPatternService()
    cmd = svc.create_command("bad",
                             lambda ctx: (_ for _ in ()).throw(ValueError("oops")))
    svc.enqueue(cmd)
    result = svc.execute_next({})
    assert result.success is False
    assert "oops" in result.error
