from app.services.app_marketplace_extension_execution_context import (
    ExecutionContextService, ExecStatus,
)
import pytest


def test_create_and_start():
    svc = ExecutionContextService()
    ctx = svc.create("ext-1", "process_data", {"items": [1, 2, 3]})
    assert ctx.status == ExecStatus.PENDING
    assert svc.start(ctx.context_id) is True
    assert ctx.status == ExecStatus.RUNNING


def test_complete():
    svc = ExecutionContextService()
    ctx = svc.create("ext-1", "transform", {"data": "input"})
    svc.start(ctx.context_id)
    svc.complete(ctx.context_id, {"result": "output"}, memory_mb=32, cpu_ms=150)
    assert ctx.status == ExecStatus.COMPLETED
    assert ctx.outputs["result"] == "output"
    assert ctx.memory_used_mb == 32


def test_fail():
    svc = ExecutionContextService()
    ctx = svc.create("ext-1", "risky_op", {})
    svc.start(ctx.context_id)
    svc.fail(ctx.context_id, "Division by zero")
    assert ctx.status == ExecStatus.FAILED
    assert "Division" in ctx.error


def test_timeout():
    svc = ExecutionContextService()
    ctx = svc.create("ext-1", "slow_op", {}, timeout_ms=1000)
    svc.start(ctx.context_id)
    svc.timeout(ctx.context_id)
    assert ctx.status == ExecStatus.TIMEOUT
    assert "1000ms" in ctx.error


def test_cancel():
    svc = ExecutionContextService()
    ctx = svc.create("ext-1", "op", {})
    assert svc.cancel(ctx.context_id) is True
    assert ctx.status == ExecStatus.CANCELLED


def test_input_too_large():
    svc = ExecutionContextService()
    with pytest.raises(ValueError, match="too large"):
        svc.create("ext-1", "op", {"data": "x" * (1024 * 1024 + 1)})


def test_timeout_bounds():
    svc = ExecutionContextService()
    with pytest.raises(ValueError, match="too long"):
        svc.create("ext-1", "op", {}, timeout_ms=999999)
    with pytest.raises(ValueError, match="too short"):
        svc.create("ext-1", "op", {}, timeout_ms=10)


def test_stats():
    svc = ExecutionContextService()
    for _ in range(3):
        ctx = svc.create("ext-1", "fn", {})
        svc.start(ctx.context_id)
        svc.complete(ctx.context_id, {})
    ctx2 = svc.create("ext-1", "fn", {})
    svc.start(ctx2.context_id)
    svc.fail(ctx2.context_id, "err")
    stats = svc.get_stats("ext-1")
    assert stats["completed"] == 3
    assert stats["failed"] == 1
