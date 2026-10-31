from app.services.app_marketplace_process_manager import ProcessManager, ProcessState


def test_start_and_stop():
    pm = ProcessManager()
    proc, msg = pm.start("p1", "ext-1", "org-1")
    assert proc is not None
    assert proc.state == ProcessState.RUNNING
    assert pm.stop("p1") is True
    assert pm.get_process("p1").state == ProcessState.STOPPED


def test_duplicate_prevented():
    pm = ProcessManager()
    pm.start("p1", "ext-1", "org-1")
    proc, msg = pm.start("p2", "ext-1", "org-1")
    assert proc is None
    assert "already running" in msg


def test_max_concurrent():
    pm = ProcessManager(max_concurrent=2)
    pm.start("a", "ext-a", "org-1")
    pm.start("b", "ext-b", "org-1")
    proc, msg = pm.start("c", "ext-c", "org-1")
    assert proc is None
    assert "Max concurrent" in msg


def test_crash():
    pm = ProcessManager()
    pm.start("p2", "ext-2", "org-2")
    assert pm.crash("p2", "SegFault") is True
    proc = pm.get_process("p2")
    assert proc.state == ProcessState.CRASHED
    assert proc.exit_code == 1


def test_timeout():
    pm = ProcessManager()
    pm.start("p3", "ext-3", "org-3", timeout_seconds=30)
    assert pm.timeout("p3") is True
    assert pm.get_process("p3").state == ProcessState.TIMED_OUT
    assert "30s" in pm.get_process("p3").error


def test_resource_update():
    pm = ProcessManager()
    pm.start("p4", "ext-4", "org-4")
    pm.update_resources("p4", cpu=45.2, memory_mb=128.5)
    proc = pm.get_process("p4")
    assert proc.cpu_usage == 45.2
    assert proc.memory_mb == 128.5


def test_list_running():
    pm = ProcessManager()
    pm.start("r1", "ext-a", "org-1")
    pm.start("r2", "ext-b", "org-1")
    pm.stop("r2")
    running = pm.list_running()
    assert len(running) == 1
    assert running[0].process_id == "r1"
