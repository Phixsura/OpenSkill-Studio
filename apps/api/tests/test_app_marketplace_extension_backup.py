from app.services.app_marketplace_extension_backup import ExtensionBackupService


def test_create_and_restore():
    bs = ExtensionBackupService()
    data = {"config": {"theme": "dark"}, "permissions": ["read"]}
    snap = bs.create_snapshot("s1", "ext-1", "org-1", "admin", data)
    assert snap.size_bytes > 0
    restored = bs.restore_snapshot("s1")
    assert restored == data
    assert bs.get_snapshot("s1").restored is True


def test_data_isolation():
    bs = ExtensionBackupService()
    original = {"key": "original"}
    bs.create_snapshot("s2", "ext-2", "org-1", "admin", original)
    original["key"] = "modified"  # mutate original
    restored = bs.restore_snapshot("s2")
    assert restored["key"] == "original"  # snapshot is isolated


def test_list_and_delete():
    bs = ExtensionBackupService()
    bs.create_snapshot("s3", "ext-3", "org-1", "admin", {"v": 1})
    bs.create_snapshot("s4", "ext-3", "org-1", "admin", {"v": 2})
    assert len(bs.list_snapshots("ext-3")) == 2
    bs.delete_snapshot("s3")
    assert len(bs.list_snapshots("ext-3")) == 1


def test_compare_snapshots():
    bs = ExtensionBackupService()
    bs.create_snapshot("c1", "ext-4", "org-1", "admin", {"a": 1, "b": 2, "c": 3})
    bs.create_snapshot("c2", "ext-4", "org-1", "admin", {"a": 1, "b": 99, "d": 4})
    diff = bs.compare_snapshots("c1", "c2")
    assert "d" in diff["added"]
    assert "c" in diff["removed"]
    assert "b" in diff["changed"]
    assert "a" in diff["unchanged"]


def test_retention_limit():
    bs = ExtensionBackupService(max_snapshots_per_ext=3)
    for i in range(5):
        bs.create_snapshot(f"r{i}", "ext-5", "org-1", "admin", {"i": i})
    assert len(bs.list_snapshots("ext-5")) == 3
