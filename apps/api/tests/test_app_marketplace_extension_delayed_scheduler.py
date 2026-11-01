from app.services.app_marketplace_extension_delayed_scheduler import DelayedSchedulerService
import time


def test_schedule_and_tick():
    svc = DelayedSchedulerService()
    now = time.time()
    svc.schedule_at("send_email", now - 1, {"to": "user@test.com"})
    executed = svc.tick(now)
    assert len(executed) == 1
    assert executed[0]["handler"] == "send_email"


def test_future_task_not_fired():
    svc = DelayedSchedulerService()
    now = time.time()
    svc.schedule_at("future", now + 100, {})
    executed = svc.tick(now)
    assert len(executed) == 0
    assert svc.pending_count() == 1


def test_ordering():
    svc = DelayedSchedulerService()
    now = time.time()
    svc.schedule_at("third", now + 3)
    svc.schedule_at("first", now + 1)
    svc.schedule_at("second", now + 2)
    executed = svc.tick(now + 3)
    handlers = [e["handler"] for e in executed]
    assert handlers == ["first", "second", "third"]


def test_cancel():
    svc = DelayedSchedulerService()
    now = time.time()
    task = svc.schedule_at("cancel_me", now - 1)
    svc.cancel(task.task_id)
    executed = svc.tick(now)
    assert len(executed) == 0


def test_repeating_task():
    svc = DelayedSchedulerService()
    now = time.time()
    svc.schedule_at("heartbeat", now - 1, repeat_interval=10)
    executed = svc.tick(now)
    assert len(executed) == 1
    assert executed[0].get("next_fire") is not None
    # Task re-scheduled
    assert svc.pending_count() == 1


def test_retry_on_failure():
    svc = DelayedSchedulerService()
    now = time.time()
    svc.schedule_at("flaky", now - 1, max_retries=2)

    def failing_executor(task):
        raise RuntimeError("failed")

    executed = svc.tick(now, executor=failing_executor)
    assert executed[0].get("retrying") is True
    assert svc.pending_count() == 1  # re-scheduled for retry


def test_retry_exhausted():
    svc = DelayedSchedulerService()
    now = time.time()
    svc.schedule_at("doomed", now - 1, max_retries=0)

    def failing_executor(task):
        raise RuntimeError("permanent failure")

    executed = svc.tick(now, executor=failing_executor)
    assert "retrying" not in executed[0]
    assert svc.pending_count() == 0


def test_delay_convenience():
    svc = DelayedSchedulerService()
    task = svc.schedule_delay("job", 0.001)
    time.sleep(0.002)
    executed = svc.tick()
    assert len(executed) == 1


def test_next_fire_time():
    svc = DelayedSchedulerService()
    now = time.time()
    svc.schedule_at("a", now + 10)
    svc.schedule_at("b", now + 5)
    assert svc.next_fire_time() == now + 5


def test_history():
    svc = DelayedSchedulerService()
    now = time.time()
    svc.schedule_at("a", now - 1)
    svc.schedule_at("b", now - 1)
    svc.tick(now)
    assert len(svc.get_history()) == 2
