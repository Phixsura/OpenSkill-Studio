from app.services.app_marketplace_sandbox_runtime import (
    SandboxRuntime, SandboxConfig, SandboxStatus,
)


def test_execute_basic():
    rt = SandboxRuntime()
    result = rt.execute("print('hello')")
    assert result.status == SandboxStatus.COMPLETED
    assert "Executed" in result.output
    assert result.duration_ms > 0


def test_execute_empty_code():
    rt = SandboxRuntime()
    result = rt.execute("")
    assert result.status == SandboxStatus.FAILED
    assert "Empty" in result.error


def test_execute_too_large():
    cfg = SandboxConfig(max_output_bytes=10)
    rt = SandboxRuntime(config=cfg)
    result = rt.execute("x" * 100)
    assert result.status == SandboxStatus.FAILED
    assert "too large" in result.error


def test_check_permissions():
    cfg = SandboxConfig(allowed_permissions=["read_files", "write_files"])
    rt = SandboxRuntime(config=cfg)
    ok, denied = rt.check_permissions(["read_files"])
    assert ok is True
    assert denied == []
    ok2, denied2 = rt.check_permissions(["read_files", "network"])
    assert ok2 is False
    assert "network" in denied2


def test_execution_history():
    rt = SandboxRuntime()
    rt.execute("a = 1")
    rt.execute("b = 2", context={"user": "test"})
    history = rt.get_execution_history()
    assert len(history) == 2
    assert history[1]["context_keys"] == ["user"]


def test_reset():
    rt = SandboxRuntime()
    rt.execute("x = 1")
    assert len(rt.get_execution_history()) == 1
    rt.reset()
    assert len(rt.get_execution_history()) == 0
