from app.services.app_marketplace_extension_task_scheduler_v2 import (
    TaskSchedulerV2Service, ScheduledTask
)
import time


def test_basic_scheduling():
    sched = TaskSchedulerV2Service()
    sched.submit(ScheduledTask("t1", "Task 1"))
    actions = sched.schedule()
    assert any(a["action"] == "started" for a in actions)


def test_edf_ordering():
    sched = TaskSchedulerV2Service(total_cpu=10)
    now = time.time()
    sched.submit(ScheduledTask("late", "Late", deadline=now + 100))
    sched.submit(ScheduledTask("urgent", "Urgent", deadline=now + 10))
    actions = sched.schedule()
    started = [a["task"] for a in actions if a["action"] == "started"]
    assert started.index("urgent") < started.index("late")


def test_dependency_wait():
    sched = TaskSchedulerV2Service()
    sched.submit(ScheduledTask("build", "Build"))
    sched.submit(ScheduledTask("test", "Test", dependencies=["build"]))
    actions = sched.schedule()
    started = [a["task"] for a in actions if a["action"] == "started"]
    assert "build" in started
    assert "test" not in started  # waiting for build
    sched.complete("build")
    actions2 = sched.schedule()
    started2 = [a["task"] for a in actions2 if a["action"] == "started"]
    assert "test" in started2


def test_resource_constraint():
    sched = TaskSchedulerV2Service(total_cpu=2)
    sched.submit(ScheduledTask("big", "Big", cpu_required=2))
    sched.submit(ScheduledTask("small", "Small", cpu_required=1))
    sched.schedule()
    # big takes all CPU, small can't start
    assert sched._tasks["big"].status == "running"
    assert sched._tasks["small"].status == "pending"


def test_preemption():
    sched = TaskSchedulerV2Service(total_cpu=2)
    sched.submit(ScheduledTask("low", "Low Priority", priority=10, cpu_required=2))
    sched.schedule()
    assert sched._tasks["low"].status == "running"
    # Higher priority task arrives
    sched.submit(ScheduledTask("high", "High Priority", priority=1, cpu_required=2))
    sched.schedule()
    assert sched._tasks["high"].status == "running"
    assert sched._tasks["low"].status == "pending"  # preempted


def test_deadline_miss():
    sched = TaskSchedulerV2Service(total_cpu=0)  # no CPU available
    sched.submit(ScheduledTask("t1", "Task", deadline=time.time() - 1))  # already past
    actions = sched.schedule()
    assert any(a["action"] == "deadline_missed" for a in actions)


def test_complete():
    sched = TaskSchedulerV2Service()
    sched.submit(ScheduledTask("t1", "Task"))
    sched.schedule()
    assert sched.complete("t1") is True
    assert sched._tasks["t1"].status == "completed"


def test_status():
    sched = TaskSchedulerV2Service(total_cpu=4, total_memory_mb=1024)
    sched.submit(ScheduledTask("t1", "A", cpu_required=1, memory_mb=256))
    sched.submit(ScheduledTask("t2", "B", cpu_required=2, memory_mb=512))
    sched.schedule()
    status = sched.get_status()
    assert status["cpu_used"] == 3
    assert status["memory_used"] == 768
