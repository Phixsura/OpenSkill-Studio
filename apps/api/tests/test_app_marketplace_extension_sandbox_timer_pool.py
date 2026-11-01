from app.services.app_marketplace_extension_sandbox_timer_pool import (
    SandboxTimerPoolService, TimerType, TimerState,
)
import time


def test_set_timeout():
    svc = SandboxTimerPoolService()
    timer = svc.set_timeout("sb-1", "on_ready", 5000)
    assert timer.timer_type == TimerType.TIMEOUT
    assert timer.state == TimerState.ACTIVE


def test_set_interval():
    svc = SandboxTimerPoolService()
    timer = svc.set_interval("sb-1", "poll", 1000)
    assert timer.timer_type == TimerType.INTERVAL


def test_interval_min_delay():
    svc = SandboxTimerPoolService()
    result = svc.set_interval("sb-1", "fast", 50)
    assert isinstance(result, dict) and "error" in result


def test_tick_fires_timeout():
    svc = SandboxTimerPoolService()
    timer = svc.set_timeout("sb-1", "cb", 100)
    timer.next_fire_at = time.time() - 1  # already due
    fired = svc.tick()
    assert len(fired) == 1
    assert timer.state == TimerState.FIRED


def test_tick_interval_reschedules():
    svc = SandboxTimerPoolService()
    timer = svc.set_interval("sb-1", "poll", 500)
    timer.next_fire_at = time.time() - 1
    svc.tick()
    assert timer.state == TimerState.ACTIVE  # still active
    assert timer.fire_count == 1
    assert timer.next_fire_at > time.time()  # rescheduled


def test_interval_max_fires():
    svc = SandboxTimerPoolService()
    timer = svc.set_interval("sb-1", "poll", 500, max_fires=2)
    timer.next_fire_at = time.time() - 1
    svc.tick()
    timer.next_fire_at = time.time() - 1
    svc.tick()
    assert timer.state == TimerState.FIRED
    assert timer.fire_count == 2


def test_cancel():
    svc = SandboxTimerPoolService()
    timer = svc.set_timeout("sb-1", "cb", 5000)
    assert svc.cancel(timer.timer_id) is True
    assert timer.state == TimerState.CANCELLED


def test_clear_all():
    svc = SandboxTimerPoolService()
    svc.set_timeout("sb-1", "a", 1000)
    svc.set_interval("sb-1", "b", 2000)
    svc.set_timeout("sb-2", "c", 1000)
    cleared = svc.clear_all("sb-1")
    assert cleared == 2
    assert svc.get_active_count("sb-1") == 0
    assert svc.get_active_count("sb-2") == 1


def test_timer_limit():
    svc = SandboxTimerPoolService()
    for i in range(100):
        svc.set_timeout("sb-1", f"cb_{i}", 5000)
    result = svc.set_timeout("sb-1", "overflow", 1000)
    assert isinstance(result, dict) and "limit" in result["error"]
