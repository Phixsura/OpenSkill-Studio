"""Tests for Consumer API Diff Analyzer service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_diff_analyzer import (
    DiffAnalyzer, ResponseSnapshot,
)


class TestDiffAnalyzer:
    def test_no_changes(self):
        svc = DiffAnalyzer()
        svc.store_snapshot(ResponseSnapshot("s1", "ep1", "v1", 200, {"id": 1, "name": "a"}))
        svc.store_snapshot(ResponseSnapshot("s2", "ep1", "v2", 200, {"id": 1, "name": "a"}))
        diff = svc.diff("ep1", "v1", "v2")
        assert diff["total_changes"] == 0
        assert diff["breaking"] is False

    def test_added_field(self):
        svc = DiffAnalyzer()
        svc.store_snapshot(ResponseSnapshot("s1", "ep1", "v1", 200, {"id": 1}))
        svc.store_snapshot(ResponseSnapshot("s2", "ep1", "v2", 200, {"id": 1, "email": "a@b.com"}))
        diff = svc.diff("ep1", "v1", "v2")
        assert "email" in diff["added_fields"]
        assert diff["breaking"] is False

    def test_removed_field_breaking(self):
        svc = DiffAnalyzer()
        svc.store_snapshot(ResponseSnapshot("s1", "ep1", "v1", 200, {"id": 1, "name": "a"}))
        svc.store_snapshot(ResponseSnapshot("s2", "ep1", "v2", 200, {"id": 1}))
        diff = svc.diff("ep1", "v1", "v2")
        assert "name" in diff["removed_fields"]
        assert diff["breaking"] is True

    def test_type_change_breaking(self):
        svc = DiffAnalyzer()
        svc.store_snapshot(ResponseSnapshot("s1", "ep1", "v1", 200, {"count": 5}))
        svc.store_snapshot(ResponseSnapshot("s2", "ep1", "v2", 200, {"count": "five"}))
        diff = svc.diff("ep1", "v1", "v2")
        assert len(diff["type_changes"]) == 1
        assert diff["breaking"] is True

    def test_value_change(self):
        svc = DiffAnalyzer()
        svc.store_snapshot(ResponseSnapshot("s1", "ep1", "v1", 200, {"status": "active"}))
        svc.store_snapshot(ResponseSnapshot("s2", "ep1", "v2", 200, {"status": "enabled"}))
        diff = svc.diff("ep1", "v1", "v2")
        assert len(diff["value_changes"]) == 1

    def test_status_code_change(self):
        svc = DiffAnalyzer()
        svc.store_snapshot(ResponseSnapshot("s1", "ep1", "v1", 200, {"ok": True}))
        svc.store_snapshot(ResponseSnapshot("s2", "ep1", "v2", 201, {"ok": True}))
        diff = svc.diff("ep1", "v1", "v2")
        assert diff["status_code_changed"] is True
        assert diff["breaking"] is True

    def test_nested_field(self):
        svc = DiffAnalyzer()
        svc.store_snapshot(ResponseSnapshot("s1", "ep1", "v1", 200, {"user": {"name": "a"}}))
        svc.store_snapshot(ResponseSnapshot("s2", "ep1", "v2", 200, {"user": {"name": "a", "age": 30}}))
        diff = svc.diff("ep1", "v1", "v2")
        assert "user.age" in diff["added_fields"]

    def test_missing_snapshot(self):
        svc = DiffAnalyzer()
        svc.store_snapshot(ResponseSnapshot("s1", "ep1", "v1", 200, {}))
        with pytest.raises(ValueError):
            svc.diff("ep1", "v1", "v99")

    def test_list_snapshots(self):
        svc = DiffAnalyzer()
        svc.store_snapshot(ResponseSnapshot("s1", "ep1", "v1", 200, {}))
        svc.store_snapshot(ResponseSnapshot("s2", "ep2", "v1", 200, {}))
        assert len(svc.list_snapshots(endpoint_id="ep1")) == 1

    def test_isolation(self):
        a, b = DiffAnalyzer(), DiffAnalyzer()
        a.store_snapshot(ResponseSnapshot("s1", "ep1", "v1", 200, {}))
        assert b.get_stats()["total_snapshots"] == 0
