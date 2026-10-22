from app.services.app_log_pruner import prune_logs

def test_prune_excess():
    logs = [{"timestamp": "2026-01-01T00:00:00Z"} for _ in range(1500)]
    r = prune_logs(logs, max_entries=1000)
    assert r["kept"] == 1000
    assert r["pruned"] == 500

def test_no_prune():
    logs = [{"timestamp": "2026-01-01T00:00:00Z"} for _ in range(10)]
    r = prune_logs(logs)
    assert r["pruned"] == 0

def test_empty():
    r = prune_logs([])
    assert r["kept"] == 0
