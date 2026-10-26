from app.services.app_marketplace_extension_sandbox_process import (
    SandboxProcessService, ProcessState,
)


def test_spawn_process():
    svc = SandboxProcessService()
    proc = svc.spawn("sb-1", "node index.js")
    assert isinstance(proc, object)
    assert proc.state == ProcessState.RUNNING


def test_forbidden_command():
    svc = SandboxProcessService()
    result = svc.spawn("sb-1", "rm -rf /")
    assert isinstance(result, dict)
    assert "Forbidden" in result["error"]


def test_process_limit():
    svc = SandboxProcessService()
    for i in range(10):
        svc.spawn("sb-1", f"worker-{i}")
    result = svc.spawn("sb-1", "worker-11")
    assert isinstance(result, dict)
    assert "limit" in result["error"]


def test_kill():
    svc = SandboxProcessService()
    proc = svc.spawn("sb-1", "server")
    assert svc.kill(proc.pid) is True
    assert proc.state == ProcessState.KILLED


def test_pause_resume():
    svc = SandboxProcessService()
    proc = svc.spawn("sb-1", "worker")
    svc.pause(proc.pid)
    assert proc.state == ProcessState.PAUSED
    svc.resume(proc.pid)
    assert proc.state == ProcessState.RUNNING


def test_kill_all():
    svc = SandboxProcessService()
    svc.spawn("sb-1", "a")
    svc.spawn("sb-1", "b")
    svc.spawn("sb-2", "c")
    killed = svc.kill_all("sb-1")
    assert killed == 2
    assert len(svc.list_processes("sb-1", ProcessState.RUNNING)) == 0


def test_stats():
    svc = SandboxProcessService()
    p1 = svc.spawn("sb-1", "worker")
    svc.update_metrics(p1.pid, 25.0, 128.0)
    stats = svc.get_stats("sb-1")
    assert stats["running"] == 1
    assert stats["total_cpu"] == 25.0
    assert stats["total_memory_mb"] == 128.0
