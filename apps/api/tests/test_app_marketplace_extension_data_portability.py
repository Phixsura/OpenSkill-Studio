from app.services.app_marketplace_extension_data_portability import (
    DataPortabilityService, ExportFormat, ConflictStrategy, ImportStatus,
)
import json
import pytest


def test_export_data():
    svc = DataPortabilityService()
    svc.store_data("ext-1", "settings", [{"id": "s1", "key": "theme", "value": "dark"}])
    svc.store_data("ext-1", "users", [{"id": "u1", "name": "Alice"}, {"id": "u2", "name": "Bob"}])
    job = svc.export_data("ext-1", ["settings", "users"])
    assert job.record_count == 3
    parsed = json.loads(job.data)
    assert len(parsed["settings"]) == 1
    assert len(parsed["users"]) == 2


def test_export_invalid_type():
    svc = DataPortabilityService()
    with pytest.raises(ValueError, match="Invalid data type"):
        svc.export_data("ext-1", ["passwords"])


def test_validate_import():
    svc = DataPortabilityService()
    ok, errs = svc.validate_import('{"settings": [{"id": "s1"}]}')
    assert ok is True
    ok2, errs2 = svc.validate_import("not json")
    assert ok2 is False
    assert "Invalid JSON" in errs2


def test_import_skip_conflicts():
    svc = DataPortabilityService()
    svc.store_data("ext-1", "settings", [{"id": "s1", "key": "old"}])
    data = json.dumps({"settings": [{"id": "s1", "key": "new"}, {"id": "s2", "key": "added"}]})
    job = svc.import_data("ext-1", data, ConflictStrategy.SKIP)
    assert job.status == ImportStatus.COMPLETED
    assert job.imported == 1
    assert job.skipped == 1


def test_import_overwrite():
    svc = DataPortabilityService()
    svc.store_data("ext-1", "users", [{"id": "u1", "name": "Old"}])
    data = json.dumps({"users": [{"id": "u1", "name": "New"}]})
    job = svc.import_data("ext-1", data, ConflictStrategy.OVERWRITE)
    assert job.imported == 1
    assert svc._extension_data["ext-1"]["users"][-1]["name"] == "New"


def test_import_rename():
    svc = DataPortabilityService()
    svc.store_data("ext-1", "content", [{"id": "c1", "text": "orig"}])
    data = json.dumps({"content": [{"id": "c1", "text": "dup"}]})
    job = svc.import_data("ext-1", data, ConflictStrategy.RENAME)
    assert job.imported == 1
    ids = [r["id"] for r in svc._extension_data["ext-1"]["content"]]
    assert "c1_imported" in ids


def test_import_invalid_fails():
    svc = DataPortabilityService()
    job = svc.import_data("ext-1", "broken json")
    assert job.status == ImportStatus.FAILED
    assert len(job.errors) > 0
