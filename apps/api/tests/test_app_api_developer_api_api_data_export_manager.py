import pytest
from app.services.app_api_developer_api_api_data_export_manager import AppAPIDeveloperAPIApiDataExportManager

class TestDataExportManager:
    def test_create(self):
        m = AppAPIDeveloperAPIApiDataExportManager()
        j = m.create("inst-1", "j1", "usage", "csv")
        assert j.status == "pending"

    def test_invalid_type(self):
        m = AppAPIDeveloperAPIApiDataExportManager()
        with pytest.raises(ValueError):
            m.create("inst-1", "j1", "secrets", "csv")

    def test_lifecycle(self):
        m = AppAPIDeveloperAPIApiDataExportManager()
        m.create("inst-1", "j1", "logs", "json")
        m.start("inst-1", "j1")
        j = m.complete("inst-1", "j1", 50000, 2_097_152)
        assert j.status == "completed"
        assert j.row_count == 50000

    def test_list_by_status(self):
        m = AppAPIDeveloperAPIApiDataExportManager()
        m.create("inst-1", "j1", "usage", "csv")
        m.create("inst-1", "j2", "logs", "json")
        m.complete("inst-1", "j1", 100, 1024)
        assert len(m.list_jobs("inst-1", "completed")) == 1
        assert len(m.list_jobs("inst-1", "pending")) == 1

    def test_isolation(self):
        m = AppAPIDeveloperAPIApiDataExportManager()
        m.create("inst-1", "j1", "usage", "csv")
        assert len(m.list_jobs("inst-2")) == 0
