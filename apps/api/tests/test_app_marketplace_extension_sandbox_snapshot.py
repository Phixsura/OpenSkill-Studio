from app.services.app_marketplace_extension_sandbox_snapshot import (
    SandboxSnapshotService,
)


def test_capture_and_list():
    svc = SandboxSnapshotService()
    snap = svc.capture("sb-1", "before deploy",
                       files={"/app/index.js": b"console.log('hello')"},
                       created_by="admin")
    assert snap.snapshot_id.startswith("snap_")
    listed = svc.list_snapshots("sb-1")
    assert len(listed) == 1
    assert listed[0]["label"] == "before deploy"


def test_restore():
    svc = SandboxSnapshotService()
    snap = svc.capture("sb-1", "v1",
                       files={"/a.txt": b"hello"},
                       env_vars={"EXT_KEY": "val"})
    restored = svc.restore(snap.snapshot_id)
    assert restored is not None
    assert restored["files"]["/a.txt"] == b"hello"
    assert restored["env_vars"]["EXT_KEY"] == "val"


def test_compare():
    svc = SandboxSnapshotService()
    s1 = svc.capture("sb-1", "v1", files={"/a.txt": b"old", "/b.txt": b"keep"})
    s2 = svc.capture("sb-1", "v2", files={"/a.txt": b"new", "/c.txt": b"added"})
    diff = svc.compare(s1.snapshot_id, s2.snapshot_id)
    assert "/c.txt" in diff["added"]
    assert "/b.txt" in diff["removed"]
    assert "/a.txt" in diff["modified"]


def test_delete():
    svc = SandboxSnapshotService()
    snap = svc.capture("sb-1", "tmp", files={"/x": b"y"})
    assert svc.delete(snap.snapshot_id) is True
    assert len(svc.list_snapshots("sb-1")) == 0


def test_max_snapshots():
    svc = SandboxSnapshotService()
    for i in range(12):
        svc.capture("sb-1", f"snap-{i}", files={f"/{i}": b"x"})
    assert len(svc.list_snapshots("sb-1")) == 10  # max per sandbox


def test_size_limit():
    svc = SandboxSnapshotService()
    big = b"x" * (51 * 1024 * 1024)
    result = svc.capture("sb-1", "huge", files={"/big": big})
    assert isinstance(result, dict)
    assert "error" in result


def test_restore_not_found():
    svc = SandboxSnapshotService()
    assert svc.restore("nonexistent") is None
