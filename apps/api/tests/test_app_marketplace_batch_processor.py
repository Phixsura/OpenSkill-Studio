from app.services.app_marketplace_batch_processor import (
    BatchProcessor, BatchStatus,
)


def test_create_and_execute():
    bp = BatchProcessor()
    job, msg = bp.create_job("j1", "install", [
        {"action": "install", "target": "ext-1"},
        {"action": "install", "target": "ext-2"},
    ])
    assert job is not None
    result = bp.execute("j1")
    assert result.status == BatchStatus.COMPLETED
    assert result.progress == 100


def test_empty_batch_rejected():
    bp = BatchProcessor()
    job, msg = bp.create_job("j2", "update", [])
    assert job is None
    assert "Empty" in msg


def test_max_batch_size():
    bp = BatchProcessor(max_batch_size=2)
    items = [{"action": "a", "target": f"t{i}"} for i in range(5)]
    job, msg = bp.create_job("j3", "update", items)
    assert job is None
    assert "exceeds" in msg


def test_partial_completion():
    bp = BatchProcessor()
    bp.create_job("j4", "migrate", [
        {"action": "migrate", "target": "a"},
        {"action": "migrate", "target": "b"},
        {"action": "migrate", "target": "c"},
    ])
    def processor(action, target):
        if target == "b":
            return False, "Migration failed for b"
        return True, "OK"
    result = bp.execute("j4", processor)
    assert result.status == BatchStatus.PARTIALLY_COMPLETED


def test_all_fail():
    bp = BatchProcessor()
    bp.create_job("j5", "delete", [{"action": "delete", "target": "x"}])
    result = bp.execute("j5", lambda a, t: (False, "denied"))
    assert result.status == BatchStatus.FAILED


def test_progress():
    bp = BatchProcessor()
    bp.create_job("j6", "notify", [
        {"action": "notify", "target": "u1"},
        {"action": "notify", "target": "u2"},
    ])
    bp.execute("j6")
    progress = bp.get_progress("j6")
    assert progress["completed"] == 2
    assert progress["failed"] == 0
    assert progress["progress"] == 100
