from app.services.app_marketplace_extension_data_pipeline import (
    DataPipelineService, PipelineStatus,
)
import pytest


def test_create_pipeline():
    svc = DataPipelineService()
    p = svc.create("ext-1", "User Import", [
        {"name": "extract", "type": "extract"},
        {"name": "validate", "type": "validate", "config": {"required_fields": ["name", "email"]}},
        {"name": "load", "type": "load"},
    ])
    assert len(p.stages) == 3
    assert p.status == PipelineStatus.IDLE


def test_execute_pipeline():
    svc = DataPipelineService()
    p = svc.create("ext-1", "ETL", [
        {"name": "pass", "type": "extract"},
    ])
    result = svc.execute(p.pipeline_id, [{"a": 1}, {"b": 2}])
    assert result["ok"] is True
    assert result["records"] == 2
    assert p.run_count == 1


def test_filter_stage():
    svc = DataPipelineService()
    p = svc.create("ext-1", "Filter", [
        {"name": "filter_active", "type": "filter", "config": {"field": "active", "value": True}},
    ])
    data = [{"name": "a", "active": True}, {"name": "b", "active": False}, {"name": "c", "active": True}]
    result = svc.execute(p.pipeline_id, data)
    assert result["records"] == 2


def test_validate_stage():
    svc = DataPipelineService()
    p = svc.create("ext-1", "Validate", [
        {"name": "check", "type": "validate", "config": {"required_fields": ["email"]}},
    ])
    data = [{"email": "a@b.com"}, {"name": "no email"}, {"email": "c@d.com"}]
    result = svc.execute(p.pipeline_id, data)
    assert result["records"] == 2


def test_transform_rename():
    svc = DataPipelineService()
    p = svc.create("ext-1", "Rename", [
        {"name": "rename", "type": "transform", "config": {"rename": {"user_name": "author"}}},
    ])
    result = svc.execute(p.pipeline_id, [{"user_name": "alice", "id": 1}])
    assert result["ok"] is True
    assert p.total_records == 1


def test_chained_stages():
    svc = DataPipelineService()
    p = svc.create("ext-1", "Chain", [
        {"name": "extract", "type": "extract"},
        {"name": "filter", "type": "filter", "config": {"field": "status", "value": "active"}},
        {"name": "validate", "type": "validate", "config": {"required_fields": ["name"]}},
    ])
    data = [
        {"name": "a", "status": "active"},
        {"name": "b", "status": "inactive"},
        {"status": "active"},  # missing name
    ]
    result = svc.execute(p.pipeline_id, data)
    assert result["records"] == 1


def test_empty_pipeline_rejected():
    svc = DataPipelineService()
    with pytest.raises(ValueError, match="at least one"):
        svc.create("ext-1", "Empty", [])


def test_stage_metrics():
    svc = DataPipelineService()
    p = svc.create("ext-1", "Metrics", [
        {"name": "filter", "type": "filter", "config": {"field": "ok", "value": True}},
    ])
    svc.execute(p.pipeline_id, [{"ok": True}, {"ok": False}])
    assert p.stages[0].records_in == 2
    assert p.stages[0].records_out == 1
    assert p.stages[0].status == "completed"
