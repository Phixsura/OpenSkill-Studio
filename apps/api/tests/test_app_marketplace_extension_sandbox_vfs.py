from app.services.app_marketplace_extension_sandbox_vfs import (
    SandboxVFSService,
)
import pytest


def test_write_and_read():
    svc = SandboxVFSService()
    svc.create_sandbox("sb-1")
    svc.write_file("sb-1", "/app/index.js", b"console.log('hello')")
    data = svc.read_file("sb-1", "/app/index.js")
    assert data == b"console.log('hello')"


def test_list_dir():
    svc = SandboxVFSService()
    svc.create_sandbox("sb-1")
    svc.write_file("sb-1", "/src/a.js", b"a")
    svc.write_file("sb-1", "/src/b.js", b"bb")
    entries = svc.list_dir("sb-1", "/src")
    assert len(entries) == 2
    names = {e["name"] for e in entries}
    assert names == {"a.js", "b.js"}


def test_delete():
    svc = SandboxVFSService()
    svc.create_sandbox("sb-1")
    svc.write_file("sb-1", "/tmp/test.txt", b"data")
    assert svc.delete("sb-1", "/tmp/test.txt") is True
    with pytest.raises(FileNotFoundError):
        svc.read_file("sb-1", "/tmp/test.txt")


def test_path_traversal_blocked():
    svc = SandboxVFSService()
    svc.create_sandbox("sb-1")
    with pytest.raises(ValueError, match="traversal"):
        svc.write_file("sb-1", "/app/../../etc/passwd", b"evil")


def test_file_size_limit():
    svc = SandboxVFSService()
    svc.create_sandbox("sb-1")
    with pytest.raises(ValueError, match="too large"):
        svc.write_file("sb-1", "/big.bin", b"x" * (11 * 1024 * 1024))


def test_relative_path_rejected():
    svc = SandboxVFSService()
    svc.create_sandbox("sb-1")
    with pytest.raises(ValueError, match="absolute"):
        svc.write_file("sb-1", "relative/path.txt", b"data")


def test_usage_tracking():
    svc = SandboxVFSService()
    svc.create_sandbox("sb-1")
    svc.write_file("sb-1", "/a.txt", b"hello")
    usage = svc.get_usage("sb-1")
    assert usage["used_bytes"] == 5
    assert usage["max_bytes"] == 100 * 1024 * 1024
