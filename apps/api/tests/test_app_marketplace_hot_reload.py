from app.services.app_marketplace_hot_reload import (
    HotReloadManager, FileChange, ReloadStatus,
)


def test_start_and_stop_session():
    hrm = HotReloadManager()
    session = hrm.start_session("s1", "ext-1", ["src/", "tests/"])
    assert session.status == ReloadStatus.WATCHING
    assert hrm.stop_session("s1") is True
    assert hrm.get_session("s1").status == ReloadStatus.IDLE


def test_record_change_and_reload():
    hrm = HotReloadManager()
    hrm.start_session("s2", "ext-2", ["src/"])
    hrm.record_change("s2", FileChange("src/main.py", "modified"))
    hrm.record_change("s2", FileChange("src/utils.py", "created"))
    result = hrm.trigger_reload("s2")
    assert result is not None
    assert result["changes_processed"] == 2
    assert result["reload_number"] == 1
    assert hrm.get_pending_changes("s2") == []


def test_ignore_patterns():
    hrm = HotReloadManager()
    hrm.start_session("s3", "ext-3", ["src/"])
    assert hrm.record_change("s3", FileChange("src/__pycache__/mod.pyc", "modified")) is False
    assert hrm.record_change("s3", FileChange("src/main.py", "modified")) is True


def test_no_reload_without_changes():
    hrm = HotReloadManager()
    hrm.start_session("s4", "ext-4", ["src/"])
    assert hrm.trigger_reload("s4") is None


def test_list_active_sessions():
    hrm = HotReloadManager()
    hrm.start_session("s5", "ext-5", ["src/"])
    hrm.start_session("s6", "ext-6", ["src/"])
    hrm.stop_session("s6")
    active = hrm.list_active_sessions()
    assert len(active) == 1
    assert active[0].session_id == "s5"


def test_multiple_reloads():
    hrm = HotReloadManager()
    hrm.start_session("s7", "ext-7", ["src/"])
    hrm.record_change("s7", FileChange("src/a.py", "modified"))
    hrm.trigger_reload("s7")
    hrm.record_change("s7", FileChange("src/b.py", "modified"))
    result = hrm.trigger_reload("s7")
    assert result["reload_number"] == 2
