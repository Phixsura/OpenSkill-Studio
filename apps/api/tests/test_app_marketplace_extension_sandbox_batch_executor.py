from app.services.app_marketplace_extension_sandbox_batch_executor import (
    SandboxBatchExecutorService, BatchStatus,
)


def test_create_batch():
    svc = SandboxBatchExecutorService()
    batch = svc.create_batch("sb-1", [
        {"name": "create_user", "params": {"name": "Alice"}},
        {"name": "create_user", "params": {"name": "Bob"}},
    ])
    assert len(batch.operations) == 2
    assert batch.status == BatchStatus.PENDING


def test_execute_all_success():
    svc = SandboxBatchExecutorService()
    batch = svc.create_batch("sb-1", [{"name": "op1"}, {"name": "op2"}])
    svc.execute(batch.batch_id, [
        {"success": True, "result": {"id": 1}},
        {"success": True, "result": {"id": 2}},
    ])
    assert batch.status == BatchStatus.COMPLETED
    summary = svc.get_summary(batch.batch_id)
    assert summary["succeeded"] == 2


def test_partial_failure():
    svc = SandboxBatchExecutorService()
    batch = svc.create_batch("sb-1", [{"name": "a"}, {"name": "b"}, {"name": "c"}])
    svc.execute(batch.batch_id, [
        {"success": True}, {"success": False, "error": "db error"}, {"success": True},
    ])
    assert batch.status == BatchStatus.PARTIAL
    summary = svc.get_summary(batch.batch_id)
    assert summary["succeeded"] == 2
    assert summary["failed"] == 1


def test_stop_on_error():
    svc = SandboxBatchExecutorService()
    batch = svc.create_batch("sb-1", [{"name": "a"}, {"name": "b"}, {"name": "c"}],
                             stop_on_error=True)
    svc.execute(batch.batch_id, [
        {"success": True}, {"success": False, "error": "fail"}, {"success": True},
    ])
    summary = svc.get_summary(batch.batch_id)
    assert summary["skipped"] == 1  # c was skipped


def test_all_failed():
    svc = SandboxBatchExecutorService()
    batch = svc.create_batch("sb-1", [{"name": "a"}, {"name": "b"}])
    svc.execute(batch.batch_id, [
        {"success": False}, {"success": False},
    ])
    assert batch.status == BatchStatus.FAILED


def test_empty_batch_rejected():
    svc = SandboxBatchExecutorService()
    result = svc.create_batch("sb-1", [])
    assert isinstance(result, dict) and "error" in result


def test_batch_too_large():
    svc = SandboxBatchExecutorService()
    result = svc.create_batch("sb-1", [{"name": f"op{i}"} for i in range(101)])
    assert isinstance(result, dict) and "too large" in result["error"]


def test_double_execute_rejected():
    svc = SandboxBatchExecutorService()
    batch = svc.create_batch("sb-1", [{"name": "a"}])
    svc.execute(batch.batch_id, [{"success": True}])
    result = svc.execute(batch.batch_id, [{"success": True}])
    assert isinstance(result, dict) and "already" in result["error"]
