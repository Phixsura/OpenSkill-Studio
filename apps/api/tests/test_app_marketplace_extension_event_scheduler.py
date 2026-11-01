from app.services.app_marketplace_extension_event_scheduler import (
    EventSchedulerService, ScheduleStatus, ScheduleType,
)
import time
import pytest


def test_schedule_once():
    svc = EventSchedulerService()
    ev = svc.schedule_once("ext-1", "cleanup", "run_cleanup", time.time() + 60)
    assert ev.schedule_type == ScheduleType.ONCE
    assert ev.status == ScheduleStatus.ACTIVE


def test_execute_once_completes():
    svc = EventSchedulerService()
    ev = svc.schedule_once("ext-1", "task", "do_thing", time.time())
    result = svc.execute(ev.event_id)
    assert result["executed"] is True
    assert ev.status == ScheduleStatus.COMPLETED


def test_recurring_continues():
    svc = EventSchedulerService()
    ev = svc.schedule_recurring("ext-1", "sync", "run_sync", 300)
    svc.execute(ev.event_id)
    assert ev.status == ScheduleStatus.ACTIVE
    assert ev.run_count == 1


def test_recurring_max_runs():
    svc = EventSchedulerService()
    ev = svc.schedule_recurring("ext-1", "report", "gen_report", 60, max_runs=2)
    svc.execute(ev.event_id)
    svc.execute(ev.event_id)
    assert ev.status == ScheduleStatus.COMPLETED


def test_failure_tracking():
    svc = EventSchedulerService()
    ev = svc.schedule_recurring("ext-1", "sync", "run_sync", 60, max_runs=0)
    for _ in range(3):
        svc.execute(ev.event_id, success=False)
    assert ev.status == ScheduleStatus.FAILED


def test_pause_resume():
    svc = EventSchedulerService()
    ev = svc.schedule_recurring("ext-1", "task", "do", 120)
    assert svc.pause(ev.event_id) is True
    assert ev.status == ScheduleStatus.PAUSED
    assert svc.resume(ev.event_id) is True
    assert ev.status == ScheduleStatus.ACTIVE


def test_min_interval():
    svc = EventSchedulerService()
    with pytest.raises(ValueError, match="60 seconds"):
        svc.schedule_recurring("ext-1", "fast", "tick", 10)


def test_due_events():
    svc = EventSchedulerService()
    svc.schedule_once("ext-1", "past", "run", time.time() - 10)
    svc.schedule_once("ext-1", "future", "run", time.time() + 9999)
    due = svc.get_due_events()
    assert len(due) == 1
    assert due[0].name == "past"
