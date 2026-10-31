"""Tests for App Data Export Manager — lifecycle, expiry, filters."""

import pytest

from app.services.app_data_export import (
    AppDataExportManager,
    ExportFormat,
    ExportStatus,
)


class TestRequestExport:
    def test_create(self):
        m = AppDataExportManager()
        e = m.request_export("inst-1", "exp-1", "users", ExportFormat.CSV)
        assert e.export_id == "exp-1"
        assert e.format == ExportFormat.CSV
        assert e.status == ExportStatus.PENDING

    def test_with_filters(self):
        m = AppDataExportManager()
        e = m.request_export("inst-1", "exp-1", "events", filters={"since": "2026-01-01"})
        assert e.filters == {"since": "2026-01-01"}

    def test_duplicate_export_id(self):
        m = AppDataExportManager()
        m.request_export("inst-1", "exp-1", "users")
        with pytest.raises(ValueError, match="already exists"):
            m.request_export("inst-1", "exp-1", "users")

    def test_missing_resource_type(self):
        m = AppDataExportManager()
        with pytest.raises(ValueError, match="resource_type"):
            m.request_export("inst-1", "exp-1", "")

    def test_missing_installation_id(self):
        m = AppDataExportManager()
        with pytest.raises(ValueError, match="installation_id"):
            m.request_export("", "exp-1", "users")


class TestLifecycle:
    def test_full_lifecycle(self):
        m = AppDataExportManager()
        m.request_export("inst-1", "exp-1", "users")
        m.start_processing("inst-1", "exp-1")
        e = m.complete_export("inst-1", "exp-1", "https://s3/export.csv",
                              file_size_bytes=1024, row_count=50)
        assert e.status == ExportStatus.COMPLETED
        assert e.file_url == "https://s3/export.csv"
        assert e.file_size_bytes == 1024
        assert e.row_count == 50

    def test_cannot_start_completed(self):
        m = AppDataExportManager()
        m.request_export("inst-1", "exp-1", "users")
        m.start_processing("inst-1", "exp-1")
        m.complete_export("inst-1", "exp-1", "https://s3/f.csv")
        with pytest.raises(ValueError, match="Cannot start"):
            m.start_processing("inst-1", "exp-1")

    def test_cannot_complete_pending(self):
        m = AppDataExportManager()
        m.request_export("inst-1", "exp-1", "users")
        with pytest.raises(ValueError, match="Cannot complete"):
            m.complete_export("inst-1", "exp-1", "https://s3/f.csv")

    def test_complete_requires_url(self):
        m = AppDataExportManager()
        m.request_export("inst-1", "exp-1", "users")
        m.start_processing("inst-1", "exp-1")
        with pytest.raises(ValueError, match="file_url"):
            m.complete_export("inst-1", "exp-1", "")


class TestFailure:
    def test_fail_pending(self):
        m = AppDataExportManager()
        m.request_export("inst-1", "exp-1", "users")
        e = m.fail_export("inst-1", "exp-1", error="timeout")
        assert e.status == ExportStatus.FAILED
        assert e.error_message == "timeout"

    def test_fail_processing(self):
        m = AppDataExportManager()
        m.request_export("inst-1", "exp-1", "users")
        m.start_processing("inst-1", "exp-1")
        e = m.fail_export("inst-1", "exp-1")
        assert e.status == ExportStatus.FAILED

    def test_cannot_fail_completed(self):
        m = AppDataExportManager()
        m.request_export("inst-1", "exp-1", "users")
        m.start_processing("inst-1", "exp-1")
        m.complete_export("inst-1", "exp-1", "https://s3/f.csv")
        with pytest.raises(ValueError, match="Cannot fail"):
            m.fail_export("inst-1", "exp-1")


class TestExpiry:
    def test_cleanup_expired(self):
        m = AppDataExportManager(expiry_hours=1)
        m.request_export("inst-1", "exp-1", "users")
        m.start_processing("inst-1", "exp-1")
        m.complete_export("inst-1", "exp-1", "https://s3/f.csv")
        e = m.get_export("inst-1", "exp-1")
        future = e.expires_at + 1
        count = m.cleanup_expired(now=future)
        assert count == 1
        e2 = m.get_export("inst-1", "exp-1")
        assert e2.status == ExportStatus.EXPIRED
        assert e2.file_url is None

    def test_cleanup_keeps_fresh(self):
        m = AppDataExportManager(expiry_hours=24)
        m.request_export("inst-1", "exp-1", "users")
        m.start_processing("inst-1", "exp-1")
        m.complete_export("inst-1", "exp-1", "https://s3/f.csv")
        e = m.get_export("inst-1", "exp-1")
        count = m.cleanup_expired(now=e.completed_at + 1)
        assert count == 0


class TestListExports:
    def test_list_newest_first(self):
        m = AppDataExportManager()
        m.request_export("inst-1", "exp-1", "users")
        m.request_export("inst-1", "exp-2", "events")
        exports = m.list_exports("inst-1")
        assert exports[0].export_id == "exp-2"

    def test_list_limit(self):
        m = AppDataExportManager()
        for i in range(5):
            m.request_export("inst-1", f"exp-{i}", "users")
        assert len(m.list_exports("inst-1", limit=3)) == 3


class TestIsolation:
    def test_cross_installation(self):
        m = AppDataExportManager()
        m.request_export("inst-1", "exp-1", "users")
        with pytest.raises(KeyError):
            m.get_export("inst-2", "exp-1")

    def test_list_scoped(self):
        m = AppDataExportManager()
        m.request_export("inst-1", "exp-1", "users")
        m.request_export("inst-2", "exp-2", "users")
        assert len(m.list_exports("inst-1")) == 1
