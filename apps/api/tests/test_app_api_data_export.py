"""Tests for App API Data Export — create, complete, fail."""

import pytest
from app.services.app_api_data_export import AppAPIDataExport, ExportStatus


class TestCreate:
    def test_create(self):
        e = AppAPIDataExport()
        ex = e.create("inst-1", "e1", "csv", "users")
        assert ex.status == ExportStatus.PENDING

    def test_invalid_format(self):
        e = AppAPIDataExport()
        with pytest.raises(ValueError):
            e.create("inst-1", "e1", "xlsx", "users")


class TestLifecycle:
    def test_complete(self):
        e = AppAPIDataExport()
        e.create("inst-1", "e1", "json", "users")
        ex = e.complete("inst-1", "e1", 1024000, 5000)
        assert ex.status == ExportStatus.COMPLETED
        assert ex.record_count == 5000

    def test_fail(self):
        e = AppAPIDataExport()
        e.create("inst-1", "e1", "csv", "users")
        ex = e.fail("inst-1", "e1")
        assert ex.status == ExportStatus.FAILED


class TestIsolation:
    def test_cross(self):
        e = AppAPIDataExport()
        e.create("inst-1", "e1", "json", "users")
        assert e.list_exports("inst-2") == []
