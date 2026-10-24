from app.services.app_marketplace_app_app_app_app_app_app_app_middleware_chain import MiddlewareChain

def test_chain():
    mc = MiddlewareChain()
    mc.use("auth", lambda ctx: {"user": "alice"}, order=1)
    mc.use("logging", lambda ctx: {"logged": True}, order=0)
    mc.use("rate_limit", lambda ctx: {"limited": False}, order=2)
    r = mc.execute({"method": "GET"})
    assert r["completed"]
    assert len(r["middlewares_applied"]) == 3
    assert r["context"]["user"] == "alice"
    assert mc.list() == ["logging", "auth", "rate_limit"]

def test_abort():
    mc = MiddlewareChain()
    mc.use("auth", lambda ctx: {"_abort": True, "status": 401})
    mc.use("handler", lambda ctx: {"result": "ok"})
    r = mc.execute({})
    assert not r["completed"]
    assert len(r["middlewares_applied"]) == 1
