from app.services.app_marketplace_extension_actor_model import ActorModelService


def _echo_handler(ctx, msg):
    ctx.state["last"] = msg.content
    if msg.msg_type == "ask":
        ctx.reply({"echo": msg.content})


def _counter_handler(ctx, msg):
    if "count" not in ctx.state:
        ctx.state["count"] = 0
    if msg.content.get("action") == "increment":
        ctx.state["count"] += msg.content.get("amount", 1)
    if msg.msg_type == "ask":
        ctx.reply({"count": ctx.state["count"]})


def test_spawn_and_tell():
    svc = ActorModelService()
    svc.spawn("echo", _echo_handler)
    assert svc.tell("echo", {"text": "hello"}) is True
    svc.process("echo")
    assert svc._actors["echo"].state["last"]["text"] == "hello"


def test_ask_pattern():
    svc = ActorModelService()
    svc.spawn("echo", _echo_handler)
    reply = svc.ask("echo", {"value": 42})
    assert reply == {"echo": {"value": 42}}


def test_counter_actor():
    svc = ActorModelService()
    svc.spawn("counter", _counter_handler)
    svc.tell("counter", {"action": "increment", "amount": 5})
    svc.tell("counter", {"action": "increment", "amount": 3})
    svc.process("counter", max_messages=10)
    reply = svc.ask("counter", {"action": "get"})
    assert reply["count"] == 8


def test_dead_letter():
    svc = ActorModelService()
    assert svc.tell("nonexistent", {"x": 1}) is False
    assert len(svc._dead_letters) == 1


def test_supervision_restart():
    svc = ActorModelService()
    def bad_handler(ctx, msg):
        raise RuntimeError("crash")
    svc.spawn("crasher", bad_handler, supervision="restart")
    svc.tell("crasher", {"trigger": "crash"})
    svc.process("crasher")
    # Should still be running after restart
    assert svc._actors["crasher"].status == "running"
    assert svc._actors["crasher"].errors == 1


def test_supervision_stop():
    svc = ActorModelService()
    def bad_handler(ctx, msg):
        raise RuntimeError("fatal")
    svc.spawn("crasher", bad_handler, supervision="stop")
    svc.tell("crasher", {"x": 1})
    svc.process("crasher")
    assert svc._actors["crasher"].status == "stopped"


def test_parent_child_stop():
    svc = ActorModelService()
    svc.spawn("parent", _echo_handler)
    svc.spawn("child1", _echo_handler, parent="parent")
    svc.spawn("child2", _echo_handler, parent="parent")
    svc.stop("parent")
    assert svc._actors["child1"].status == "stopped"
    assert svc._actors["child2"].status == "stopped"


def test_actor_to_actor():
    svc = ActorModelService()
    received = []
    def receiver(ctx, msg):
        received.append(msg.content)
    def sender(ctx, msg):
        ctx.tell("receiver", {"forwarded": True})
    svc.spawn("receiver", receiver)
    svc.spawn("sender", sender)
    svc.tell("sender", {"trigger": True})
    svc.process("sender")
    svc.process("receiver")
    assert {"forwarded": True} in received


def test_stats():
    svc = ActorModelService()
    svc.spawn("a", _echo_handler)
    svc.spawn("b", _echo_handler)
    svc.tell("a", {"x": 1})
    svc.process("a")
    stats = svc.get_stats()
    assert stats["total_actors"] == 2
    assert stats["running"] == 2
    assert stats["total_processed"] == 1
