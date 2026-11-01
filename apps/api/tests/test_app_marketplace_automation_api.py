from app.services.app_marketplace_automation_api import (
    AutomationEngine, TriggerType, WorkflowStatus,
)


def test_create_and_get():
    engine = AutomationEngine()
    wf = engine.create_workflow(
        "wf-001", "On Submit Review", TriggerType.EVENT,
        {"event": "submission.created"},
        [{"action": "notify", "params": {"channel": "#reviews"}}],
        owner="alice",
    )
    assert wf.workflow_id == "wf-001"
    assert wf.status == WorkflowStatus.DRAFT
    assert len(wf.steps) == 1
    fetched = engine.get_workflow("wf-001")
    assert fetched is not None
    assert fetched.name == "On Submit Review"


def test_activate_and_trigger():
    engine = AutomationEngine()
    engine.create_workflow(
        "wf-002", "Deploy Pipeline", TriggerType.WEBHOOK,
        {"url": "/hooks/deploy"},
        [{"action": "build"}, {"action": "test"}, {"action": "deploy"}],
        owner="bob",
    )
    engine.activate("wf-002")
    assert engine.get_workflow("wf-002").status == WorkflowStatus.ACTIVE
    run = engine.trigger("wf-002", {"branch": "main"})
    assert run is not None
    assert run["result"] == "success"
    assert run["steps_executed"] == 3


def test_pause():
    engine = AutomationEngine()
    engine.create_workflow("wf-003", "Nightly", TriggerType.SCHEDULE,
                           {"cron": "0 0 * * *"}, [{"action": "cleanup"}], owner="ops")
    engine.activate("wf-003")
    assert engine.pause("wf-003") is True
    assert engine.get_workflow("wf-003").status == WorkflowStatus.PAUSED


def test_trigger_inactive_fails():
    engine = AutomationEngine()
    engine.create_workflow("wf-004", "Draft", TriggerType.MANUAL,
                           {}, [{"action": "run"}], owner="test")
    result = engine.trigger("wf-004")
    assert result is None  # can't trigger a draft


def test_list_and_run_log():
    engine = AutomationEngine()
    engine.create_workflow("wf-010", "A", TriggerType.EVENT, {}, [{"action": "a"}], owner="x")
    engine.create_workflow("wf-011", "B", TriggerType.EVENT, {}, [{"action": "b"}], owner="y")
    assert len(engine.list_workflows()) == 2
    assert len(engine.list_workflows(owner="x")) == 1
    engine.activate("wf-010")
    engine.trigger("wf-010")
    engine.trigger("wf-010")
    log = engine.get_run_log("wf-010")
    assert len(log) == 2
    assert log[1]["run_number"] == 2
