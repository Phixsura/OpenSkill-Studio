from app.services.app_marketplace_extension_sandbox_request_interceptor import (
    SandboxRequestInterceptorService, InterceptPhase, InterceptAction,
)


def test_register_and_list():
    svc = SandboxRequestInterceptorService()
    svc.register("sb-1", "logger", InterceptPhase.BEFORE, InterceptAction.PASS)
    assert len(svc.list_interceptors("sb-1")) == 1


def test_before_pass():
    svc = SandboxRequestInterceptorService()
    svc.register("sb-1", "logger", InterceptPhase.BEFORE, InterceptAction.PASS)
    results = svc.execute_before("sb-1", {"url": "/api/data"})
    assert len(results) == 1
    assert results[0].action == InterceptAction.PASS


def test_block():
    svc = SandboxRequestInterceptorService()
    svc.register("sb-1", "blocker", InterceptPhase.BEFORE, InterceptAction.BLOCK,
                 config={"url_pattern": "blocked.com"})
    results = svc.execute_before("sb-1", {"url": "https://blocked.com/api"})
    assert results[0].blocked is True


def test_block_stops_chain():
    svc = SandboxRequestInterceptorService()
    svc.register("sb-1", "blocker", InterceptPhase.BEFORE, InterceptAction.BLOCK,
                 config={"url_pattern": "evil"}, order=0)
    svc.register("sb-1", "logger", InterceptPhase.BEFORE, InterceptAction.PASS, order=1)
    results = svc.execute_before("sb-1", {"url": "https://evil.com"})
    assert len(results) == 1  # second interceptor not reached


def test_delay():
    svc = SandboxRequestInterceptorService()
    svc.register("sb-1", "slow", InterceptPhase.BEFORE, InterceptAction.DELAY,
                 config={"delay_ms": 500})
    results = svc.execute_before("sb-1", {"url": "/api"})
    assert results[0].delay_ms == 500


def test_after_interceptor():
    svc = SandboxRequestInterceptorService()
    svc.register("sb-1", "cache", InterceptPhase.AFTER, InterceptAction.CACHE)
    results = svc.execute_after("sb-1", {"url": "/api"}, {"status": 200})
    assert results[0].cached is True


def test_toggle():
    svc = SandboxRequestInterceptorService()
    i = svc.register("sb-1", "test", InterceptPhase.BEFORE, InterceptAction.PASS)
    svc.toggle("sb-1", i.interceptor_id)
    results = svc.execute_before("sb-1", {})
    assert len(results) == 0  # disabled


def test_execution_count():
    svc = SandboxRequestInterceptorService()
    i = svc.register("sb-1", "counter", InterceptPhase.BEFORE, InterceptAction.PASS)
    svc.execute_before("sb-1", {})
    svc.execute_before("sb-1", {})
    assert i.execution_count == 2
