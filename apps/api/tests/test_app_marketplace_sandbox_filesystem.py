import pytest
from app.services.app_marketplace_sandbox_filesystem import SandboxFileSystem


def test_write_and_read():
    fs = SandboxFileSystem()
    fs.write_file("hello.txt", "Hello, World!")
    content = fs.read_file("hello.txt")
    assert content == b"Hello, World!"


def test_path_traversal_blocked():
    fs = SandboxFileSystem()
    with pytest.raises(PermissionError, match="traversal"):
        fs.write_file("../../etc/passwd", "hack")


def test_file_size_limit():
    fs = SandboxFileSystem(max_file_size=100)
    with pytest.raises(ValueError, match="max size"):
        fs.write_file("big.txt", "x" * 200)


def test_total_size_limit():
    fs = SandboxFileSystem(max_total_size=500)
    fs.write_file("a.txt", "x" * 200)
    fs.write_file("b.txt", "y" * 200)
    with pytest.raises(ValueError, match="limit exceeded"):
        fs.write_file("c.txt", "z" * 200)


def test_mkdir_and_listdir():
    fs = SandboxFileSystem()
    fs.mkdir("src")
    fs.write_file("src/main.py", "print('hi')")
    fs.write_file("src/utils.py", "# utils")
    entries = fs.listdir("/sandbox/src")
    assert "main.py" in entries
    assert "utils.py" in entries


def test_delete():
    fs = SandboxFileSystem()
    fs.write_file("temp.txt", "delete me")
    assert fs.exists("temp.txt") is True
    fs.delete_file("temp.txt")
    assert fs.exists("temp.txt") is False


def test_stat():
    fs = SandboxFileSystem()
    fs.write_file("data.json", '{"key": "value"}')
    info = fs.stat("data.json")
    assert info["size"] == 16
    assert info["is_directory"] is False


def test_cannot_delete_root():
    fs = SandboxFileSystem()
    with pytest.raises(PermissionError):
        fs.delete_file("/sandbox")
