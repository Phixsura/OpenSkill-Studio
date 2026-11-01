from app.services.app_marketplace_extension_middleware_chain import (
    MiddlewareChainService, Context
)


def test_basic_chain():
    chain = MiddlewareChainService()
    chain.use("first", lambda ctx, next: (ctx.state.update({"a": 1}), next()))
    chain.use("second", lambda ctx, next: (ctx.state.update({"b": 2}), next()))
    ctx = chain.execute()
    assert ctx.state == {"a": 1, "b": 2}


def test_onion_model():
    """Middleware wraps inner layers like an onion."""
    order = []
    def outer(ctx, next):
        order.append("outer-before")
        next()
        order.append("outer-after")
    def inner(ctx, next):
        order.append("inner")
        next()

    chain = MiddlewareChainService()
    chain.use("outer", outer, priority=10)
    chain.use("inner", inner, priority=1)
    chain.execute()
    assert order == ["outer-before", "inner", "outer-after"]


def test_short_circuit():
    chain = MiddlewareChainService()
    chain.use("auth", lambda ctx, next: ctx.response.update({"status": 401}))  # no next()
    chain.use("handler", lambda ctx, next: ctx.response.update({"status": 200}))
    ctx = chain.execute()
    assert ctx.response["status"] == 401  # handler never reached


def test_request_modification():
    chain = MiddlewareChainService()
    def add_user(ctx, next):
        ctx.request["user"] = "alice"
        next()
    def handler(ctx, next):
        ctx.response["greeting"] = f"Hello {ctx.request['user']}"
        next()
    chain.use("auth", add_user, priority=10)
    chain.use("handler", handler)
    ctx = chain.execute(Context(request={}))
    assert ctx.response["greeting"] == "Hello alice"


def test_conditional_middleware():
    chain = MiddlewareChainService()
    chain.use("logging", lambda ctx, next: (ctx.state.update({"logged": True}), next()),
              condition=lambda ctx: ctx.request.get("verbose"))
    chain.use("handler", lambda ctx, next: next())

    # Without verbose — logging skipped
    ctx1 = chain.execute(Context(request={}))
    assert "logged" not in ctx1.state

    # With verbose — logging runs
    ctx2 = chain.execute(Context(request={"verbose": True}))
    assert ctx2.state["logged"] is True


def test_error_handling():
    chain = MiddlewareChainService()
    chain.use("failing", lambda ctx, next: (_ for _ in ()).throw(RuntimeError("crash")))
    chain.use_error("error_handler", lambda ctx: ctx.response.update({"error": ctx.error}))
    ctx = chain.execute()
    assert ctx.error == "crash"
    assert ctx.response["error"] == "crash"


def test_abort():
    chain = MiddlewareChainService()
    def aborter(ctx, next):
        ctx.aborted = True
        ctx.response["reason"] = "rate limited"
    chain.use("rate_limit", aborter, priority=10)
    chain.use("handler", lambda ctx, next: ctx.response.update({"ok": True}))
    ctx = chain.execute()
    assert ctx.aborted is True
    assert "ok" not in ctx.response


def test_timing():
    chain = MiddlewareChainService()
    chain.use("fast", lambda ctx, next: next())
    ctx = chain.execute()
    assert "fast" in ctx.timings
    assert ctx.timings["fast"] >= 0


def test_chain_listing():
    chain = MiddlewareChainService()
    chain.use("auth", lambda ctx, next: next(), priority=10)
    chain.use("logging", lambda ctx, next: next(), priority=5)
    chain.use("handler", lambda ctx, next: next(), priority=1)
    assert chain.get_chain() == ["auth", "logging", "handler"]
