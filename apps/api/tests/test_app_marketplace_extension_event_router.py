from app.services.app_marketplace_extension_event_router import EventRouterService


def test_exact_type_match():
    er = EventRouterService()
    received = []
    er.register("handler", ["user.created"], lambda t, p: received.append(p))
    er.route("user.created", {"id": 1})
    assert len(received) == 1


def test_wildcard_type():
    er = EventRouterService()
    received = []
    er.register("handler", ["user.*"], lambda t, p: received.append(t))
    er.route("user.created", {})
    er.route("user.deleted", {})
    er.route("order.created", {})
    assert received == ["user.created", "user.deleted"]


def test_star_all():
    er = EventRouterService()
    received = []
    er.register("catch_all", ["*"], lambda t, p: received.append(t))
    er.route("anything", {})
    assert len(received) == 1


def test_content_filter():
    er = EventRouterService()
    received = []
    er.register("vip", ["order.*"], lambda t, p: received.append(p),
                content_filter={"customer.tier": "vip"})
    er.route("order.created", {"customer": {"tier": "vip"}, "amount": 100})
    er.route("order.created", {"customer": {"tier": "free"}, "amount": 10})
    assert len(received) == 1
    assert received[0]["amount"] == 100


def test_regex_content_filter():
    er = EventRouterService()
    received = []
    er.register("errors", ["log.*"], lambda t, p: received.append(p),
                content_filter={"level": "regex:^(error|fatal)$"})
    er.route("log.entry", {"level": "error", "msg": "bad"})
    er.route("log.entry", {"level": "info", "msg": "ok"})
    assert len(received) == 1


def test_priority():
    er = EventRouterService()
    order = []
    er.register("low", ["event"], lambda t, p: order.append("low"), priority=1)
    er.register("high", ["event"], lambda t, p: order.append("high"), priority=10)
    er.route("event", {})
    assert order == ["high", "low"]


def test_dead_letter():
    er = EventRouterService()
    er.register("handler", ["known.event"], lambda t, p: None)
    routed = er.route("unknown.event", {"data": 1})
    assert routed.dead_lettered is True
    assert len(er.get_dead_letters()) == 1


def test_handler_error():
    er = EventRouterService()
    er.register("bad", ["event"], lambda t, p: (_ for _ in ()).throw(RuntimeError("crash")))
    er.register("good", ["event"], lambda t, p: None)
    routed = er.route("event", {})
    assert len(routed.errors) == 1
    assert "good" in routed.handled_by


def test_unregister():
    er = EventRouterService()
    er.register("temp", ["event"], lambda t, p: None)
    assert er.unregister("temp") is True
    routed = er.route("event", {})
    assert routed.dead_lettered is True


def test_disabled_handler():
    er = EventRouterService()
    er.register("h", ["event"], lambda t, p: None)
    er._handlers[0].enabled = False
    routed = er.route("event", {})
    assert routed.dead_lettered is True


def test_stats():
    er = EventRouterService()
    er.register("h", ["event"], lambda t, p: None)
    er.route("event", {})
    er.route("other", {})
    stats = er.get_stats()
    assert stats["routed"] == 1
    assert stats["dead_lettered"] == 1
