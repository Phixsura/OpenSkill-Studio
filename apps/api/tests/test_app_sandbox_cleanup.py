from datetime import UTC, datetime, timedelta
from app.services.app_sandbox_cleanup import find_stale_executions, compute_cleanup_plan

def test_find_stale():
    old = (datetime.now(UTC) - timedelta(hours=48)).isoformat()
    execs = [{"status": "running", "created_at": old, "app_id": "a1"},
             {"status": "completed", "created_at": old, "app_id": "a2"}]
    stale = find_stale_executions(execs, max_age_hours=24)
    assert len(stale) == 1  # only running one

def test_no_stale():
    recent = datetime.now(UTC).isoformat()
    execs = [{"status": "running", "created_at": recent}]
    assert find_stale_executions(execs) == []

def test_cleanup_plan():
    stale = [{"app_id": "a1"}, {"app_id": "a1"}, {"app_id": "a2"}]
    plan = compute_cleanup_plan(stale)
    assert plan["total_stale"] == 3
    assert plan["by_app"]["a1"] == 2

def test_empty_plan():
    plan = compute_cleanup_plan([])
    assert plan["total_stale"] == 0
