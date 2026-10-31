from app.services.app_marketplace_app_sandbox_filesystem import SandboxFilesystem

def test_write_read():
    fs = SandboxFilesystem()
    fs.write("test.txt", b"hello")
    assert fs.read("test.txt") == b"hello"

def test_path_traversal():
    fs = SandboxFilesystem()
    r = fs.write("../etc/passwd", b"hack")
    assert r["error"]

def test_absolute_path():
    fs = SandboxFilesystem()
    r = fs.write("/etc/passwd", b"hack")
    assert r["error"]

def test_quota():
    fs = SandboxFilesystem(quota_bytes=10)
    r = fs.write("big.bin", b"x" * 20)
    assert r["error"]

def test_delete():
    fs = SandboxFilesystem()
    fs.write("f.txt", b"data")
    assert fs.delete("f.txt")
    assert fs.read("f.txt") is None

def test_list():
    fs = SandboxFilesystem()
    fs.write("a.txt", b"aaa")
    fs.write("b.txt", b"bb")
    files = fs.list_files()
    assert len(files) == 2
    assert files[0]["path"] == "a.txt"

def test_stats():
    fs = SandboxFilesystem(quota_bytes=1000)
    fs.write("f.txt", b"x" * 100)
    s = fs.stats()
    assert s["usage_pct"] == 10.0
