from app.services.app_marketplace_extension_workflow_trigger import (
    WorkflowTriggerService, TriggerType, TriggerStatus,
)
import pytest


def test_create_and_list():
    svc = WorkflowTriggerService()
    t = svc.create_trigger("ext-1", "wf-1", TriggerType.MANUAL, "Deploy trigger")
    assert t.trigger_id.startswith("trg_")
    assert t.trigger_type == TriggerType.MANUAL
    triggers = svc.list_triggers("ext-1")
    assert len(triggers) == 1


def test_cron_requires_expression():
    svc = WorkflowTriggerService()
    with pytest.raises(ValueError, match="cron_expression"):
        svc.create_trigger("ext-1", "wf-1", TriggerType.CRON, "Bad cron")


def test_event_requires_type():
    svc = WorkflowTriggerService()
    with pytest.raises(ValueError, match="event_type"):
        svc.create_trigger("ext-1", "wf-1", TriggerType.EVENT, "Bad event")


def test_fire_manual():
    svc = WorkflowTriggerService()
    t = svc.create_trigger("ext-1", "wf-1", TriggerType.MANUAL, "Deploy")
    result = svc.fire(t.trigger_id)
    assert result["fired"] is True
    assert result["fire_count"] == 1


def test_conditions_evaluate():
    svc = WorkflowTriggerService()
    t = svc.create_trigger("ext-1", "wf-1", TriggerType.WEBHOOK, "On push",
                           conditions=[{"field": "branch", "operator": "eq", "value": "main"}])
    result = svc.fire(t.trigger_id, {"branch": "main"})
    assert result["fired"] is True
    result2 = svc.fire(t.trigger_id, {"branch": "dev"})
    assert result2["fired"] is False


def test_pause_resume():
    svc = WorkflowTriggerService()
    t = svc.create_trigger("ext-1", "wf-1", TriggerType.MANUAL, "T")
    assert svc.pause(t.trigger_id) is True
    result = svc.fire(t.trigger_id)
    assert result["fired"] is False
    assert svc.resume(t.trigger_id) is True
    result2 = svc.fire(t.trigger_id)
    assert result2["fired"] is True


def test_invalid_operator():
    svc = WorkflowTriggerService()
    with pytest.raises(ValueError, match="Invalid operator"):
        svc.create_trigger("ext-1", "wf-1", TriggerType.WEBHOOK, "Bad",
                           conditions=[{"field": "x", "operator": "LIKE", "value": "1"}])
