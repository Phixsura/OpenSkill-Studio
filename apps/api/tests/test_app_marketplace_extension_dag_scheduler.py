from app.services.app_marketplace_extension_dag_scheduler import DagSchedulerService


def test_topological_sort():
    svc = DagSchedulerService()
    svc.add_task("compile", "Compile")
    svc.add_task("test", "Test", ["compile"])
    svc.add_task("deploy", "Deploy", ["test"])
    order = svc.topological_sort()
    assert order.index("compile") < order.index("test")
    assert order.index("test") < order.index("deploy")


def test_parallel_levels():
    svc = DagSchedulerService()
    svc.add_task("a", "A")
    svc.add_task("b", "B")
    svc.add_task("c", "C", ["a", "b"])
    svc.add_task("d", "D", ["c"])
    levels = svc.get_parallel_levels()
    assert len(levels) == 3
    assert set(levels[0]) == {"a", "b"}  # parallel
    assert levels[1] == ["c"]
    assert levels[2] == ["d"]


def test_cycle_detection():
    svc = DagSchedulerService()
    svc.add_task("a", "A", ["b"])
    svc.add_task("b", "B", ["a"])
    cycle = svc.detect_cycle()
    assert cycle is not None


def test_no_cycle():
    svc = DagSchedulerService()
    svc.add_task("a", "A")
    svc.add_task("b", "B", ["a"])
    assert svc.detect_cycle() is None


def test_topological_sort_cycle_raises():
    svc = DagSchedulerService()
    svc.add_task("x", "X", ["y"])
    svc.add_task("y", "Y", ["x"])
    try:
        svc.topological_sort()
        assert False
    except ValueError:
        pass


def test_critical_path():
    svc = DagSchedulerService()
    svc.add_task("a", "A", duration_ms=100)
    svc.add_task("b", "B", duration_ms=200)
    svc.add_task("c", "C", ["a"], duration_ms=50)
    svc.add_task("d", "D", ["b"], duration_ms=50)
    svc.add_task("e", "E", ["c", "d"], duration_ms=100)
    path, duration = svc.critical_path()
    # Critical path: b(200) → d(50) → e(100) = 350
    assert duration == 350
    assert "b" in path
    assert "e" in path


def test_diamond_dependency():
    svc = DagSchedulerService()
    svc.add_task("root", "Root")
    svc.add_task("left", "Left", ["root"])
    svc.add_task("right", "Right", ["root"])
    svc.add_task("join", "Join", ["left", "right"])
    order = svc.topological_sort()
    assert order[0] == "root"
    assert order[-1] == "join"
    levels = svc.get_parallel_levels()
    assert set(levels[1]) == {"left", "right"}


def test_ready_tasks():
    svc = DagSchedulerService()
    svc.add_task("a", "A")
    svc.add_task("b", "B", ["a"])
    svc.add_task("c", "C")
    ready = svc.get_ready_tasks()
    assert set(ready) == {"a", "c"}  # no deps
    # Complete 'a'
    svc._tasks["a"].status = "completed"
    ready = svc.get_ready_tasks()
    assert set(ready) == {"b", "c"}


def test_independent_tasks():
    svc = DagSchedulerService()
    svc.add_task("a", "A")
    svc.add_task("b", "B")
    svc.add_task("c", "C")
    levels = svc.get_parallel_levels()
    assert len(levels) == 1
    assert len(levels[0]) == 3
