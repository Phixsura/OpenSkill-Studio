from app.services.app_marketplace_extension_sandbox_log_stream import (
    SandboxLogStreamService, LogLevel,
)


def test_write_and_read():
    svc = SandboxLogStreamService()
    svc.write("sb-1", LogLevel.INFO, "Server started on port 3000")
    entries = svc.read("sb-1")
    assert len(entries) == 1
    assert entries[0].message == "Server started on port 3000"


def test_level_filter():
    svc = SandboxLogStreamService()
    svc.write("sb-1", LogLevel.DEBUG, "debug msg")
    svc.write("sb-1", LogLevel.INFO, "info msg")
    svc.write("sb-1", LogLevel.ERROR, "error msg")
    entries = svc.read("sb-1", min_level=LogLevel.ERROR)
    assert len(entries) == 1
    assert entries[0].level == LogLevel.ERROR


def test_search():
    svc = SandboxLogStreamService()
    svc.write("sb-1", LogLevel.INFO, "Connected to database")
    svc.write("sb-1", LogLevel.INFO, "Processing request")
    svc.write("sb-1", LogLevel.ERROR, "Database connection lost")
    entries = svc.read("sb-1", search="database")
    assert len(entries) == 2


def test_source_filter():
    svc = SandboxLogStreamService()
    svc.write("sb-1", LogLevel.INFO, "stdout msg", source="stdout")
    svc.write("sb-1", LogLevel.ERROR, "stderr msg", source="stderr")
    entries = svc.read("sb-1", source="stderr")
    assert len(entries) == 1


def test_error_count():
    svc = SandboxLogStreamService()
    svc.write("sb-1", LogLevel.INFO, "ok")
    svc.write("sb-1", LogLevel.ERROR, "err1")
    svc.write("sb-1", LogLevel.FATAL, "fatal1")
    assert svc.get_error_count("sb-1") == 2


def test_stats():
    svc = SandboxLogStreamService()
    for _ in range(5):
        svc.write("sb-1", LogLevel.INFO, "info")
    svc.write("sb-1", LogLevel.ERROR, "err")
    stats = svc.get_stats("sb-1")
    assert stats["total"] == 6
    assert stats["error_count"] == 1


def test_tail():
    svc = SandboxLogStreamService()
    for i in range(50):
        svc.write("sb-1", LogLevel.INFO, f"msg-{i}")
    tail = svc.tail("sb-1", 5)
    assert len(tail) == 5
    assert tail[0].message == "msg-45"


def test_clear():
    svc = SandboxLogStreamService()
    svc.write("sb-1", LogLevel.INFO, "msg")
    assert svc.clear("sb-1") == 1
    assert len(svc.read("sb-1")) == 0
