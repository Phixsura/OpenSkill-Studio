from app.services.app_marketplace_extension_snapshot_diff import SnapshotDiffService


def test_diff_files():
    sds = SnapshotDiffService()
    old = {"a.py": 100, "b.py": 200, "c.py": 300}
    new = {"a.py": 100, "b.py": 250, "d.py": 150}
    diffs = sds.diff_files(old, new)
    statuses = {d.path: d.status for d in diffs}
    assert statuses["a.py"] == "unchanged"
    assert statuses["b.py"] == "modified"
    assert statuses["c.py"] == "removed"
    assert statuses["d.py"] == "added"


def test_diff_permissions():
    sds = SnapshotDiffService()
    added, removed = sds.diff_permissions(
        ["read", "write"], ["read", "analytics", "webhooks"]
    )
    assert "analytics" in added
    assert "webhooks" in added
    assert "write" in removed


def test_diff_config():
    sds = SnapshotDiffService()
    result = sds.diff_config(
        {"theme": "dark", "timeout": 30, "debug": True},
        {"theme": "light", "timeout": 30, "verbose": False},
    )
    assert result["changed"]["theme"]["old"] == "dark"
    assert result["changed"]["theme"]["new"] == "light"
    assert "debug" in result["removed"]
    assert "verbose" in result["added"]
    assert "timeout" in result["unchanged"]


def test_full_diff_and_summary():
    sds = SnapshotDiffService()
    diff = sds.compute_full_diff(
        "ext-1", "1.0.0", "2.0.0",
        old_files={"main.py": 100}, new_files={"main.py": 150, "utils.py": 50},
        old_perms=["read"], new_perms=["read", "write"],
        old_config={"key": "old"}, new_config={"key": "new"},
    )
    summary = sds.get_summary(diff)
    assert summary["files"]["added"] == 1
    assert summary["files"]["modified"] == 1
    assert summary["permissions_added"] == 1
    assert summary["config_changes"] == 1
    assert summary["breaking"] is False  # no removed perms


def test_breaking_change_detection():
    sds = SnapshotDiffService()
    diff = sds.compute_full_diff(
        "ext-2", "1.0", "2.0",
        old_files={}, new_files={},
        old_perms=["read", "admin"], new_perms=["read"],
        old_config={"a": 1, "b": 2}, new_config={"a": 1},
    )
    summary = sds.get_summary(diff)
    assert summary["breaking"] is True  # admin removed + config "b" removed
